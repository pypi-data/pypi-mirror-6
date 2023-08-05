# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.sqlalchemy.proxy --
# :Creato:    mar 11 ago 2009 14:18:40 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt')) as f:
    VERSION = f.read().strip()

setup(
    name='metapensiero.sqlalchemy.proxy',
    version=VERSION,
    description="Expose SQLAlchemy's queries and their metadata to a webservice",
    long_description=README + '\n\n' + CHANGES,

    author='Lele Gaifax',
    author_email='lele@metapensiero.it',
    url="https://bitbucket.org/lele/metapensiero.sqlalchemy.proxy",

    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "License :: OSI Approved ::"
        " GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Database",
    ],


    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['metapensiero', 'metapensiero.sqlalchemy'],

    install_requires=[
        'setuptools',
        'sqlalchemy',
    ],

    tests_require=[
        'nose',
        'coverage',
    ],
    test_suite='nose.collector',
)
