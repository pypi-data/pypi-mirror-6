#-*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.test import test
from distutils.core import Command
import importlib
import tornado
import os
import sys


# hacks to use in setup.py to avoid
# import pyrocumulus before its build
def get_version_from_file():
    # get version number from __init__ file
    # before module is installed

    fname = 'pyrocumulus/__init__.py'
    with open(fname) as f:
        fcontent = f.readlines()
    version_line = [l for l in fcontent if 'VERSION' in l][0]
    return version_line.split('=')[1].strip().strip("'").strip('"')

def get_long_description_from_file():
    # content of README will be the long description

    fname = 'README'
    with open(fname) as f:
        fcontent = f.read()
    return fcontent

# copy/paste from pyrocumulus.setupcommands to avoid
# import pyrocumulus before its build
# the reason to have a runtornado command here is to
# run my functional tests
class RunTornadoCommand(Command):
    description = "command to start a tornado server"
    user_options = [('daemonize', None, 'run as a daemon'),
                    ('port=', None, 'port to listen'),
                    ('stdin=', None, 'stdin file'),
                    ('stdout=', None, 'stdout file'),
                    ('stderr=', None, 'stderr file'),
                    ('pidfile=', None, 'pid file for tornado'),
                    ('kill', None, 'kills tornado server')]

    application = None

    def initialize_options(self):
        module = 'functional_tests.test_autoapi'
        module = importlib.import_module(module)
        self.application = module.application
        self.daemonize = False
        self.port = 8888
        self.stdin = '/dev/null'
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
            self.redirect_file_descriptors()
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
        self._do_fork()

    def redirect_file_descriptors(self):
        for fd in sys.stdout, sys.stderr:
            fd.flush()

        self._try_create_required_dirs_and_files()
        stdin = open(self.stdin, 'r')
        stdout = open(self.stdout, 'a+')
        stderr = open(self.stderr, 'a+')

        os.dup2(stdin.fileno(), sys.stdin.fileno())
        os.dup2(stdout.fileno(), sys.stdout.fileno())
        os.dup2(stderr.fileno(), sys.stderr.fileno())

        sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr

    def _try_create_required_dirs_and_files(self):
        dirs = []
        dirs.append(os.path.dirname(self.stdin))
        dirs.append(os.path.dirname(self.stdout))
        dirs.append(os.path.dirname(self.stderr))
        
        for directory in dirs:
            try:
                os.mkdir(directory)
            except OSError:
                pass
        # creating file for stdin
        with open(self.stdin, 'w'):
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


class custom_test(test):
    # another hack to run my functional tests, now its for buildbot...
    user_options = test.user_options + [
        ('tornadoenv=', None, "run tornado on correct virtualevn"),
    ]

    def initialize_options(self):
        super(custom_test, self).initialize_options()
        self.tornadoenv = None


VERSION = get_version_from_file()
DESCRIPTION = """
Glue-code to make (even more!) easy and fun work with mongoengine an tornado
"""
LONG_DESCRIPTION = get_long_description_from_file()

setup(name='pyrocumulus',
      version=VERSION,
      author='Juca Crispim',
      author_email='jucacrispim@gmail.com',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      url='https://gitorious.org/pyrocumulus',
      packages=find_packages(exclude=['tests', 'tests.*']),
      install_requires=['tornado>=3.1.1', 'mongoengine>=0.8.4'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      test_suite='tests.__init__',
      provides=['pyrocumulus'],
      cmdclass={'runtornado': RunTornadoCommand,
                'test': custom_test})
