import os
import sys

NAME = 'ShirtsioAPI'
execfile('shirtsio/version.py')
DESCRIPTION = 'Shirts.io API for Python'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

requests = 'requests >= 0.8.8'
if sys.version_info < (2, 6):
    requests += ', < 0.10.1'
install_requires = [requests]

from shirtsio.version import VERSION

setup(name='shirtsio',
      version=VERSION,
      description=DESCRIPTION,
      author='shirtsio',
      author_email='support@shirts.io',
      url='https://github.com/ooshirts/shirtsio-python',
      packages=['shirtsio'],
      install_requires=install_requires,
      platforms='Any',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Software Development :: Libraries :: Python Modules']
)
