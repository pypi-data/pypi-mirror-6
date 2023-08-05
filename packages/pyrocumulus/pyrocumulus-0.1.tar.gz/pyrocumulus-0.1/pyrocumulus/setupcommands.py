#-*- coding: utf-8 -*-

# Copyright 2013 Juca Crispim <jucacrispim@gmail.com>

# This file is part of pyrocumulus.

# pyrocumulus is free software: you can redistribute it and/or modify	
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyrocumulus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyrocumulus.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import resource
from distutils.core import Command
import tornado.ioloop


class RunTornadoCommand(Command):
    description = "command to start a tornado server"
    user_options = [('daemonize', None, 'run as a daemon'),
                    ('port=', None, 'port to listen'),
                    ('stdout=', None, 'stdout file'),
                    ('stderr=', None, 'stderr file'),
                    ('pidfile=', None, 'pid file for tornado'),
                    ('kill', None, 'kills tornado server')]

    application = None

    def initialize_options(self):
        self.daemonize = False
        self.port = 8888
        self.stdout = 'logs/tornadostdout.log'
        self.stderr = 'logs/tornadostderr.log'
        self.pidfile = 'runtornado.pid'
        self.kill = False

    def run(self):
        if self.kill:
            return self.killtornado()

        self.application.listen(self.port)
        if self.daemonize:
            self.run_as_a_daemon()
            self.close_file_descriptors()
            self.redirect_stdout_stderr()
            self._write_to_file(self.pidfile, str(os.getpid()))

        tornado.ioloop.IOLoop.instance().start()

    def killtornado(self):
        pid = None
        try:
            pid = int(self._read_file(self.pidfile))
        except IOError:
            print('Tornado pid file not found. Exiting')
        except TypeError:
            print('Bad content on pid file. Exiting')

        if pid is None:
            return False

        os.kill(pid, 9)
        print('Tornado server killed')
        return True

    def run_as_a_daemon(self):
        self._do_fork()
        os.setsid()
        self._do_fork()

    def close_file_descriptors(self):
        """
        Closes all file descriptors left open in the process
        """
        limit = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        for fd in range(limit):
            try:
                os.close(fd)
            except OSError:
                pass
        
    def redirect_stdout_stderr(self):
        """
        Redirect stdout and stderr to /dev/null or to a
        log file
        """
        for fd in sys.stdout, sys.stderr:
            fd.flush()
    
        sys.stdout= open(self.stdout, 'a', 1)
        sys.stderr = open(self.stderr, 'a', 1)

    def _try_create_required_dirs_and_files(self):
        dirs = []
        dirs.append(os.path.dirname(self.stdout))
        dirs.append(os.path.dirname(self.stderr))
        
        for directory in dirs:
            try:
                os.mkdir(directory)
            except OSError:
                pass
        
    def _do_fork(self):
        pid = os.fork()
        if pid != 0:
            sys.exit(0)

    def _read_file(self, fname):
        with open(fname) as f:
            content = f.read()
        return content

    def _write_to_file(self, fname, content):
        with open(fname, 'w') as f:
            f.write(content)

    def finalize_options(self):
        pass


def run_tornado(application):
    RunTornadoCommand.application = application
    return RunTornadoCommand
