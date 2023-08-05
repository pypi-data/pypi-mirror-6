AUTHOR = 'Chris Dent'
AUTHOR_EMAIL = 'cdent@peermore.com'
NAME = 'tiddlywebplugins.postgresql'
DESCRIPTION = 'postgresql-based store for tiddlyweb'
VERSION = '0.1.3' # don't forget to update __init__.py too


import os

from setuptools import setup, find_packages


setup(
    namespace_packages = ['tiddlywebplugins'],
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = 'http://pypi.python.org/pypi/%s' % NAME,
    platforms = 'Posix; MacOS X; Windows',
    packages = find_packages(exclude=['test']),
    install_requires = ['setuptools',
        'tiddlyweb>=1.4.2',
        'tiddlywebplugins.sqlalchemy3>=3.1.0',
        'psycopg2',
        ],
    zip_safe = False,
    license = 'BSD'
    )
