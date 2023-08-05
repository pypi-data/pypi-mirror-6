# Created by James Darabi (mail@jdarabi.com)

from distutils.core import setup

from ystocklist import __version__, __license__

with open('README.rst') as file:
  long_description = file.read()

setup(
  py_modules = ['ystocklist'],
  name = 'ystocklist',
  version = __version__,
  author = 'James Darabi',
  author_email = 'mail@jdarabi.com',
  url = 'https://bitbucket.org/jamesdarabi/ystocklist',
  description = 'Generate a list of Yahoo stock symbols',
  long_description = long_description,
  license = __license__
)