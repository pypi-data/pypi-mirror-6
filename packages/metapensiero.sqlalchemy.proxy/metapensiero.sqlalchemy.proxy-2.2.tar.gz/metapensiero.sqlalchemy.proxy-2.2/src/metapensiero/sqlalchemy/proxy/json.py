# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.sqlalchemy.proxy -- SimpleJSON glue
# :Creato:    gio 04 dic 2008 13:56:51 CET
# :Autore:    Lele Gaifax <lele@nautilus.homeip.net>
# :Licenza:   GNU General Public License version 3 or later
#

"Minimalistic support for (simple) datetimes and decimals with SimpleJSON"

from __future__ import absolute_import

import datetime, decimal

try:
    from simplejson import JSONDecoder, JSONEncoder, dumps, loads
    from simplejson.decoder import scanstring
    from simplejson.scanner import py_make_scanner
except ImportError: # pragma: nocover
    from json import JSONDecoder, JSONEncoder, dumps, loads
    from json.decoder import scanstring
    from json.scanner import py_make_scanner


JSONDateFormat = 'Y-m-d'
JSONTimeFormat = 'H:i:s'
JSONTimestampFormat = 'Y-m-d\\TH:i:s'


def _json_datetime_or_string(s, *args, **kw):
    res, end = scanstring(s, *args, **kw)
    l = len(res)

    # Maybe a date
    if l == 10:
        chunks = res.split('-')
        if len(chunks) == 3:
            try:
                y, m, d = map(int, chunks)
            except ValueError:
                pass
            else:
                return datetime.date(y, m, d), end

    # Maybe a datetime
    if l == 19:
        pieces = res.split('T')
        if len(pieces) == 2:
            chunks = pieces[0].split('-')
            if len(chunks) == 3:
                chunks.extend(pieces[1].split(':'))
                if len(chunks) == 6:
                    try:
                        y, mo, d, h, m, s = map(int, chunks)
                    except ValueError:
                        pass
                    else:
                        return datetime.datetime(y, mo, d, h, m, s), end

    # Maybe a time
    if l == 8:
        chunks = res.split(':')
        if len(chunks) == 3:
            try:
                h, m, s = map(int, chunks)
            except ValueError:
                pass
            else:
                return datetime.time(h, m, s), end

    # Maybe a timedelta
    if l < 20:
        chunks = res.split(':')
        if len(chunks) == 4:
            try:
                d, h, m, s = map(int, chunks)
            except ValueError:
                pass
            else:
                if d<0:
                    res = -datetime.timedelta(days=-d, hours=h,
                                              minutes=m, seconds=s)
                else:
                    res = datetime.timedelta(days=d, hours=h,
                                             minutes=m, seconds=s)

    return res, end


class Decoder(JSONDecoder):
    """Extends JSONDecoder to handle date and datetime."""

    def __init__(self, encoding=None, object_hook=None, parse_float=None,
                 parse_int=None, parse_constant=None, strict=True):
        super(Decoder, self).__init__(encoding=encoding,
                                      parse_float=parse_float,
                                      parse_int=parse_int,
                                      parse_constant=parse_constant,
                                      strict=strict,
                                      object_hook=object_hook)

        self.parse_string = _json_datetime_or_string
        self.scan_once = py_make_scanner(self)


class Encoder(JSONEncoder):
    """Extends JSONEncoder for date and decimal types."""

    def push_date(self, d):
        """Serialize the given datetime.date object to a JSON string."""
        # Default is ISO 8601 compatible (standard notation).
        return "%04d-%02d-%02d" % (d.year, d.month, d.day)

    def push_timedelta(self, t):
        """Serialize the given datetime.timedelta object to a JSON string."""
        days = t.days
        if days < 0:
            minus = "-"
            days = -days - 1
            seconds = 24*60*60 - t.seconds
        else:
            minus = ""
            seconds = t.seconds
        secs = seconds % 60
        seconds /= 60
        mins = seconds % 60
        hours = seconds / 60
        return "%s%d:%02d:%02d:%02d" % (minus, days, hours, mins, secs)

    def push_time(self, t):
        """Serialize the given datetime.time object to a JSON string."""
        # Default is ISO 8601 compatible (standard notation).
        return "%02d:%02d:%02d" % (t.hour, t.minute, t.second)

    def push_datetime(self, dt):
        """Serialize the given datetime.datetime object to a JSON string."""
        # Default is ISO 8601 compatible (standard notation).
        # Don't use strftime because that can't handle dates before 1900.
        return ("%04d-%02d-%02dT%02d:%02d:%02d" %
                (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))

    def default(self, o):
        # We MUST check for a datetime.datetime instance before datetime.date.
        # datetime.datetime is a subclass of datetime.date, and therefore
        # instances of it are also instances of datetime.date.
        if isinstance(o, datetime.datetime):
            return self.push_datetime(o)
        elif isinstance(o, datetime.date):
            return self.push_date(o)
        elif isinstance(o, datetime.timedelta):
            return self.push_timedelta(o)
        elif isinstance(o, datetime.time):
            return self.push_time(o)
        elif isinstance(o, decimal.Decimal): # pragma: nocover
            return str(o)
        else:
            return JSONEncoder.default(self, o)


def py2json(data):
    return dumps(data, cls=Encoder, separators=(',', ':'))


def json2py(data, use_decimal=True):
    return loads(data, parse_float=decimal.Decimal if use_decimal else None,
                 cls=Decoder)
