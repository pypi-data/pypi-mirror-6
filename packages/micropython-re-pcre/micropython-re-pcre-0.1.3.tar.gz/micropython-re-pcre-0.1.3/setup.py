import sys
print "re setup sys.path =", sys.path
# Remove current dir from sys.path, otherwise distutils will peek up our
# module instead of system.
sys.path.pop(0)
from setuptools import setup

setup(name='micropython-re-pcre',
      version='0.1.3',
      description='re module for MicroPython, based on PCRE and FFI',
      url='https://github.com/micropython/micropython/issues/405',
      author='Paul Sokolovsky',
      author_email='micro-python@googlegroups.com',
      license='MIT',
      py_modules=['re'])
