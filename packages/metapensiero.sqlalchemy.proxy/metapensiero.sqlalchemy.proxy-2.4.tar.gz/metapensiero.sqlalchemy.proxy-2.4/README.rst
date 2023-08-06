..  -*- coding: utf-8 -*-
.. :Progetto:  metapensiero.sqlalchemy.proxy
.. :Creato:    gio 30 apr 2009 10:01:20 CEST
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

===============================
 metapensiero.sqlalchemy.proxy
===============================

Expose SQLAlchemy's queries and their metadata to a webservice
==============================================================

This package a few utilities to make it easier applying some filtering
to a stock query and obtaining the resultset in various formats.

An helper decorator explicitly designed for Pylons is included: it
provides a `property` like syntax to attach either a ProxiedQuery or a
plain Python function to a Controller, handling ``GET``, ``POST`` or
``DEL`` request methods.

Since version 1.7 there are some Pyramid specific subclasses that help
using the proxies within a Pyramid view as well as a `expose`
decorator that simplify their implementation.
