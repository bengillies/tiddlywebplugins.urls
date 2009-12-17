# YOU NEED TO EDIT THESE
AUTHOR = 'Ben Gillies'
AUTHOR_EMAIL = 'bengillies@gmail.com'
NAME = 'tiddlywebplugins.urls'
DESCRIPTION = 'Map TiddlyWeb URLs to your own custom URLs'
VERSION = '0.1'


import os

from setuptools import setup, find_packages


# You should carefully review the below (install_requires especially).
setup(
    namespace_packages = ['tiddlywebplugins'],
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = file(os.path.join(os.path.dirname(__file__), 'README')).read(),
    author = AUTHOR,
    url = 'http://pypi.python.org/pypi/%s' % NAME,
    packages = find_packages(exclude='test'),
    author_email = AUTHOR_EMAIL,
    platforms = 'Posix; MacOS X; Windows',
    install_requires = ['setuptools', 'tiddlyweb', 'tiddlywebplugins.utils',
        'selector']
    )
