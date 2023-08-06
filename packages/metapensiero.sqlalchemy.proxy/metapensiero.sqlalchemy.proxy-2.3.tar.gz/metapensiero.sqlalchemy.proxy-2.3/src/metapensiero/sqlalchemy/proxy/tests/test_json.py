# -*- coding: utf-8 -*-
#:Progetto:  metapensiero.sqlalchemy.proxy -- Test JSON utils
#:Creato:    dom 07 apr 2013 15:22:57 CEST
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from nose.tools import assert_equal, assert_raises

from metapensiero.sqlalchemy.proxy.json import json2py, py2json


def test_date_jsonification():
    d = date(1968, 3, 18)
    assert_equal(json2py(py2json(d)), d)


def test_time_jsonification():
    t = time(10, 11, 12)
    assert_equal(json2py(py2json(t)), t)


def test_datetime_jsonification():
    dt = datetime(1968, 3, 18, 10, 10, 0)
    assert_equal(json2py(py2json(dt)), dt)


def test_timedelta_jsonification():
    td = timedelta(days=7, hours=5, minutes=3, seconds=1)
    assert_equal(json2py(py2json(td)), td)

    td = timedelta(days=-7, hours=5, minutes=3, seconds=1)
    assert_equal(json2py(py2json(td)), td)


def test_decimal_jsonification():
    d = Decimal('3.1415926')
    assert_equal(json2py(py2json(d)), d)


def test_plain_strings():
    s = 'aa:bb:cc'
    assert_equal(json2py(py2json(s)), s)

    s = 'aa:bb:cc:dd'
    assert_equal(json2py(py2json(s)), s)

    s = 'aaaa-bb-cc'
    assert_equal(json2py(py2json(s)), s)

    s = 'aaaa-bb-ccTdd:ee:ff'
    assert_equal(json2py(py2json(s)), s)


def test_unjsonable():
    class Foo(object):
        pass

    f = Foo()
    assert_raises(TypeError, py2json, (f,))
