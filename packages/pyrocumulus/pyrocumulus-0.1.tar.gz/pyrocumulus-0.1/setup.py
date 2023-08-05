#-*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setup_helpers import (get_version_from_file, custom_test,
                            RunTornadoCommand, get_long_description_from_file)

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
