# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.sqlalchemy.proxy -- Query builders
# :Creato:    sab 18 ott 2008 23:59:34 CEST
# :Autore:    Lele Gaifax <lele@nautilus.homeip.net>
# :Licenza:   GNU General Public License version 3 or later
#

"""
This module implements some facilities that makes it very easy to
rework arbitrary SQLAlchemy queries applying some filter conditions,
constraining the actual selected columns, batched results, obtaining a
meta description of the resultset, eventually marshalled in JSON, or
as a list of plain dictionaries instead of the SQLAlchemy rows, and so
on.

This is the basic mechanism used in SoL, a Pylons application, to
expose an arbitrary dataset in JSON thru a ``Controller``, using the
:func:`metapensiero.sqlalchemy.proxy.pylons.proxy` decorator that
automatically glues the proxied thing to the web request. SoL's ExtJS
layer uses the meta description to build the data grids.
"""

from __future__ import absolute_import

from collections import Callable, Mapping, Sequence
from datetime import datetime
import logging

from sqlalchemy import (Boolean, Date, DateTime, Integer, Interval,
                        Numeric, and_, func, not_, or_,
                        select, String, Text, Time)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import ColumnProperty, class_mapper
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import Selectable


log = logging.getLogger(__name__)


try:
    basestring
except NameError: # pragma: nocover
    # Py3 compatibility
    basestring = str


def get_exception_message(e):
    """Extract the error message from the given exception.

    :param e: an Exception instance
    :rtype: a unicode string
    """

    msg = str(e)
    if isinstance(msg, bytes):
        for enc in ('utf-8', 'latin1'):
            try:
                msg = msg.decode(enc)
            except UnicodeDecodeError:
                pass
            else:
                break
        else:
            msg = msg.decode('utf-8', errors='replace')
    return msg


def get_adaptor_for_type(satype):
    """Create an adaptor for the given type.

    :param satype: an SQLAlchemy ``TypeEngine``
    :rtype: a function

    Create and return a function that adapts its unique argument
    to the given `satype`.
    """

    if isinstance(satype, Integer):
        coerce_value = lambda s: int(s) if s else None
    elif isinstance(satype, (Date, DateTime)):
        def coerce_date(s):
            from .json import json2py

            if isinstance(s, basestring):
                res = s and json2py('"%s"' % s) or None
            else:
                res = s
            if isinstance(satype, Date) and isinstance(s, datetime):
                res = s.date()
            return res
        coerce_value = coerce_date
    elif isinstance(satype, Boolean):
        def coerce_boolean(s):
            if isinstance(s, basestring):
                return s.lower() == 'true'
            else:
                return bool(s)
        coerce_value = coerce_boolean
    else:
        coerce_value = lambda s: s if s else None

    return coerce_value


def compare_field(field, value):
    """Build a comparison expression for the field.

    :param field: an SQLAlchemy ``Column``
    :param value: the value to compare with
    :rtype: an SQLALchemy ``Expression``

    Taking into account both the type of the field and of the value,
    create an SQLAlchemy expression usable as a filter on the field.

    If `value` is a string containing one or more commas (``,``), or a
    *sequence* (i.e. ``list`` or ``tuple``), the expression will use
    the ``IN`` operator to compare the field against all specified
    values; the string value may start with ``<>``: this negates the
    expression giving a ``NOT IN``.

    If `value` is a dictionary containing at least one of the keys
    `start` and `end`, then the expression will be something like
    ``field BETWEEN :start AND :end``, if both values are present, or
    ``field >= :start`` if `end` is not given or ``None``, otherwise
    ``field <= :end``.

    `value` can be prefixed with ``>=``, ``>``, ``=``, ``<``, ``<=`` o
    ``<>``, with the obvious meaning. ``~=value`` is translated into
    ``field ILIKE value%``. If the prefix is ``~``, or not recognized,
    the generated filter expression will be ``field ILIKE %value%``.

    Finally, `value` can be ``NULL`` to mean ``field IS NULL``,
    or ``!NULL`` or even ``<>NULL`` with the opposit meaning.
    """

    try:
        ftype = field.type
        if hasattr(ftype, 'impl'):
            ftype = ftype.impl

        coerce_value = get_adaptor_for_type(ftype)

        if value is None:
            return field == None

        # Handle ranges, either a dictionary value with "start" or "end"
        # keys, or a string value in the form "start-value><end-value"

        if isinstance(value, basestring) and '><' in value:
            start, end = value.split('><')
            value = {'start': start, 'end': end}

        if isinstance(value, Mapping) and ('start' in value or 'end' in value):
            start = coerce_value(value.get('start', None))
            end = coerce_value(value.get('end', None))
            if start is not None and end is not None:
                return field.between(start, end)
            elif start is not None:
                return field >= start
            elif end is not None:
                return field <= end
            else:
                raise UserWarning('Range ends cannot be both None')

        if isinstance(value, basestring):
            if ',' in value:
                if value.startswith('<>'):
                    value = value[2:]
                    return not_(field.in_([coerce_value(v) for v in value.split(',')]))
                else:
                    return field.in_([coerce_value(v) for v in value.split(',')])

            if value == 'NULL':
                return field == None
            elif value == '!NULL' or value == '<>NULL':
                return field != None
            elif value.startswith('~='):
                value = value[2:]
                return field.ilike(value+'%')
            elif value.startswith('~'):
                value = value[1:]
                return field.ilike('%'+value+'%')
            elif value.startswith('>='):
                value = value[2:]
                return field >= coerce_value(value)
            elif value.startswith('>'):
                value = value[1:]
                return field > coerce_value(value)
            elif value.startswith('<='):
                value = value[2:]
                return field <= coerce_value(value)
            elif value.startswith('<>'):
                value = value[2:]
                return field != coerce_value(value)
            elif value.startswith('<'):
                value = value[1:]
                return field < coerce_value(value)
            elif value.startswith('='):
                value = value[1:]
                return field == coerce_value(value)
            elif isinstance(ftype, String):
                return field.ilike('%'+value+'%')
            else:
                return field == coerce_value(value)
        elif isinstance(value, Sequence):
            return field.in_([coerce_value(v) for v in value])
        else:
            return field == coerce_value(value)
    except Exception as e:
        log.error(u'Error comparing field "%s" with value "%s": %s',
                  field.name, value, e)
        raise


def col_by_name(query, colname):
    "Helper: find the (first) columns with the given name."

    # First look in the selected columns
    for c in query.inner_columns:
        if c.name == colname:
            return c
    # Then in the froms
    for f in query.froms:
        c = f.columns.get(colname)
        if c is not None:
            return c

        papables = [c for c in f.columns if c.key == colname]
        if len(papables)>=1:
            c = papables[0]
            if len(papables)>1:
                log.warning(u'Ambiguous column name "%s" for %s:'
                            u' selecting "%s"', colname, str(query), c)
            return c

        papables = [c for c in f.columns if c.name.endswith('_'+colname)]
        if len(papables)>=1:
            c = papables[0]
            if len(papables)>1:
                log.warning(u'Ambiguous column name "%s" for %s:'
                            u' selecting "%s"', colname, str(query), c)
            return c


def csv2list(csv):
    """Build a list of strings from a CSV or JSON array.

    :param csv: a string containing either a ``CSV`` or a JSON array
    :rtype: a Python list

    This is very simplicistic: since its used to transfer a list of
    field names, that is plain ASCII strings, JSON escapes are not
    even considered.

    `csv` may be either a plain CSV string such as ``first,second,third``
    or a JSON array, such as ``["first","second","third"]``.
    """

    if csv.startswith('[') and csv.endswith(']'):
        res = [v[1:-1] for v in csv[1:-1].split(',')]
    else:
        res = [v.strip() for v in csv.split(',')]
    return res


def extract_raw_conditions(args):
    """Extract raw conditions

    :param args: a dictionary, usually request.params
    :rtype: a list of tuples

    Recognize three possible syntaxes specifying filtering conditions:

    1. the old ExtJS 2 way: ?filter_col=fieldname&filter_value=1
    2. the new ExtJS 4 way where the ``filters`` argument is a JSON
       encoded array of dictionaries, each containing a ``property`` slot
       with the field name as value, an ``operator`` slot and a ``value``
       slot.
    3. a custom syntax: ?filter_fieldname=1

    Build a list of (fieldname, fieldvalue) tuples, where `fieldvalue`
    may be prefixed by the ``operator`` specified with the second
    syntax above.

    Note that the `args` parameter is **modified** in place!
    """

    missing = object()

    conditions = []

    # Old syntax:
    # ?filter_col=fieldname&filter_value=1

    fcol = args.pop('filter_col', missing)
    fvalue = args.pop('filter_value', missing)

    if fcol is not missing and fvalue is not missing:
        conditions.append((fcol, fvalue))

    # ExtJS 4 syntax:
    # filter=[{"property": "fieldname", "operator": "=", "value": "1"},...]

    filters = args.pop('filter', missing)
    if filters is missing:
        # try old name for backward compatibility
        filters = args.pop('filters', missing)

    if filters is not missing:
        if isinstance(filters, basestring):
            from .json import loads
            filters = loads(filters)

        for f in filters:
            fcol = f.get('property', missing)
            if fcol is missing:
                continue

            fvalue = f.get('value', missing)
            if fvalue is missing:
                continue

            fop = f.get('operator')
            if fop:
                if not isinstance(fvalue, basestring):
                    fvalue = str(fvalue)
                if not fvalue.startswith(fop):
                    fvalue = fop + fvalue

            conditions.append((fcol, fvalue))

    # Yet another syntax:
    # ?filter_fieldname=1

    # This is needed as we are going to change the dictionary
    fnames = list(args.keys())
    for f in fnames:
        if f.startswith('filter_'):
            fcol = f[7:]
            if not fcol:
                continue
            fvalue = args.pop(f, missing)
            if fvalue is not missing:
                conditions.append((fcol, fvalue))

    return conditions


def apply_filters(query, args):
    """Filter a given query.

    :param query: an SQLAlchemy ``Query``
    :param args: a dictionary
    :rtype: a tuple

    `query` may be either a SQL statement (not necessarily a
    ``SELECT``) or an ORM query.

    The `args` dictionary may contain some special keys, that will
    be used to build a filter expression, or to change the query
    in particular ways. All these keys will be *consumed*, that is
    removed from the `args` dictionary.

    filter_col
      the name of the field going to be filtered

    filter_value
      value of the filter

    filter_name-of-the-field
      specify both the `name-of-the-field` and the value to apply

    filter (or filters)
      a sequence of filter specifications, or a JSON string containing a list of
      dictionaries: each dictionary must contain a ``property`` and a ``value``
      slots and an optional ``operator`` which is prepended to the given value,
      if it already does not when specified

    only_cols
      filter the selected columns of the query, using only fields
      specified with this argument, assumed to be a comma separated
      list of field names

    query
      this is used combined with `fields`: if present, its value will
      be searched in the specified fields, within an ``OR`` expression

    fields
      this is a list of field names that selects which fields will be
      compared to the `query` value. Currently this functionality works
      only on ``String``\s: all fields of a different kind are ignored

    The function `compare_field()` is used to build the filter
    expressions.

    Returns a tuple with the modified query at the first slot, and another
    which is either `None` or the list of columns specified by `only_cols`.
    """

    if isinstance(query, Query):
        stmt = query.statement
    else:
        stmt = query

    rconditions = extract_raw_conditions(args)
    conditions = []

    for fcol, fvalue in rconditions:
        col = col_by_name(stmt, fcol)
        if col is not None:
            cond = compare_field(col, fvalue)
            conditions.append(cond)

    if conditions:
        if len(conditions)>1:
            fexpr = and_(*conditions)
        else:
            fexpr = conditions[0]
        if isinstance(query, Query):
            query = query.filter(fexpr)
        else:
            query = query.where(fexpr)

    qvalue = args.pop('query', None)
    only_cols = args.pop('only_cols', None)
    qfields = args.pop('fields', only_cols)

    if qvalue:
        if qfields is None:
            qfields = [c.name for c in stmt.inner_columns]
        if isinstance(qfields, basestring):
            qfields = csv2list(qfields)
        conds = []
        for fcol in qfields:
            col = col_by_name(stmt, fcol)
            if col is not None:
                ct = col.type
                if hasattr(ct, 'impl'):
                    ct = ct.impl
                if isinstance(ct, String):
                    conds.append(compare_field(col, qvalue))
        if conds:
            if len(conds)>1:
                cond = or_(*conds)
            else:
                cond = conds[0]
            if isinstance(query, Query):
                query = query.filter(cond)
            else:
                query = query.where(cond)

    if only_cols:
        if isinstance(only_cols, basestring):
            only_cols = csv2list(only_cols)
        if not isinstance(query, Query):
            cols = [col for col in [col_by_name(query, c) for c in only_cols]
                    if col is not None]
            if not cols:
                assert False, "No valid column in only_cols='%s'" % only_cols
            query = query.with_only_columns(cols)

    return query, only_cols


def apply_sorters(query, sort, dir):
    """Order a given query.

    :param query: an SQLAlchemy ``Query``
    :param sort: either a string, the name of the field, or a sequence of a
                 dictionaries (possibly a JSON encoded array), each containing
                 a ``property`` slot and a ``direction`` slot, respectively
                 the field name and the ordering direction
    :rtype: an SQLAlchemy ``Query``

    `query` may be either a SQL statement (not necessarily a
    ``SELECT``) or an ORM query.
    """

    if isinstance(sort, basestring):
        if sort.startswith('['):
            from .json import loads
            sort = loads(sort)
        else:
            sort = [{'property': sort, 'direction': dir}]

    if isinstance(query, Query):
        stmt = query.statement
    else:
        stmt = query

    for item in sort:
        property = item['property']
        direction = item.get('direction') or 'ASC'

        col = col_by_name(stmt, property)

        if col is not None:
            if direction != 'ASC':
                col = col.desc()
            query = query.order_by(col)
        else:
            log.warning(u'Requested sort on "%s", which does'
                        u' not exist in %s', property, query)

    return query


class MetaInfo(Mapping):
    "Helper class, a dictionary where values can be callables"

    def __init__(self, name, info):
        self.name = name
        if isinstance(info, Callable):
            info = info(name)
        self.info = info

    def __getitem__(self, key):
        item = self.info.get(key)
        if isinstance(item, Callable):
            item = item(self.name, key)
        return item

    def __contains__(self, key):
        return key in self.info

    def __iter__(self):
        return iter(self.info)

    def __len__(self):
        return len(self.info)


class ProxiedBase(object):
    """Abstract base for the proxy thingie"""

    def translate(self, msg):
        "Stub implementation of i18n basic functions, to be overridden."

        return msg

    def __call__(self, session, *conditions, **args):
        """Apply filter conditions, execute the query and return results.

        :param session: an SQLAlchemy ``Session``
        :param conditions: a list of SQLAlchemy expressions
        :param args: a dictionary
        :rtype: depending on the arguments, either a dictionary, a list of
                tuples or a JSON string

        The first argument is the SQLAlchemy `session`, mandatory. All
        remaining arguments are eventually used to filter and change
        the query. Unused arguments remains accessible when the query
        is finally called.

        Some keyword arguments have special meaning:

        start
          This is the start of the interested range of records

        limit
          This is the maximum number of returned records

        result
          When ``False`` or ``None`` (or the strings ``"False"``,
          ``"None"`` and ``"false"``) means that no result set will be
          returned (reasonably either `metadata` or `count` are
          given); when ``True`` (or the strings ``"True"`` and
          ``"true"``), most of the other options are ignored and
          **only** the native Python results is returned; otherwise
          it's a string, the name of the *slot* of the returned
          dictionary containing the results set.

          ``True`` by default.

        success
          If `result` is not ``True``, this is a string used as the name
          of the slot containing execution status, that will be a boolean
          flag, ``True`` to indicate successfull execution, ``False``
          otherwise.

          By default it's ``"success"``.

        message
          If `result` is not ``True``, this is a string used as the name
          of the slot containing execution message, that will either ``"Ok"``
          when everything went good, otherwise a string with a possible reason
          of the failure.

          By default it's ``"message"``.

        count
          If `result` is not ``True``, this may be a string used as the
          name of the slot containing the total number of records that
          satisfy the conditions, ignoring the eventual range
          specified with `start` and `limit`. When ``False`` or ``None``
          (the default) the count won't be computed.

        metadata
          If `result` is not ``True``, this may be the name of the slot
          containing a description of the result, in a format
          compatible with ExtJS `Store`.

          ``None``, the default, disables the feature.

        asdict
          When you want to deal with plain Python dictionaries, one
          for each row, instead of the standard SQLAlchemy
          `resultset`, set this to ``True``. ``False`` by default.

        sort
          If specified, the name of the field to sort the result by. It may be a
          sequence of dictionaries, to specify an ordering based on multiple
          columns.

        dir
          When `sort` is specified, the direction to sort with. It
          defaults to "ASC", any different value will sort in
          DESCending order.

        All these keywords are pulled (that is, removed) from the
        execution *context* of the query, as well as those used by
        `apply_filters()` function.
        """

        start = args.pop('start', None)
        if start is not None:
            start = int(start)
        limit = args.pop('limit', None)
        if limit is not None:
            limit = int(limit)

        resultslot = args.pop('result', True)
        if resultslot in ('False', 'None', 'false'):
            resultslot = False
        elif resultslot in ('True', 'true'):
            resultslot = True

        slot = args.pop('success', 'success')
        successslot = resultslot is not True and slot

        slot = args.pop('message', 'message')
        messageslot = resultslot is not True and slot

        slot = args.pop('count', None)
        countslot = resultslot is not True and slot

        slot = args.pop('metadata', None)
        metadataslot = resultslot is not True and slot

        asdict = args.pop('asdict', False)
        sort = args.pop('sort', None)
        dir = args.pop('dir', 'ASC')

        result = {}
        result[successslot] = False

        try:
            query = self.filterQueryWithArgs(session, conditions, args)
        except: # pragma: nocover
            log.exception(u"Unhandled exception applying filters"
                          u" %r and args %r", conditions, args)
            raise

        try:
            if countslot and limit != 0:
                result[countslot] = self.getCount(session, query)

            if resultslot and limit != 0:
                if sort:
                    query = apply_sorters(query, sort, dir)
                if start:
                    query = query.offset(start)
                if limit:
                    query = query.limit(limit)
                result[resultslot] = self.getResult(session, query, asdict)

            if metadataslot:
                result[metadataslot] = self.getMetadata(session, query,
                                                        countslot,
                                                        resultslot,
                                                        successslot)

            result[successslot] = True
            result[messageslot] = 'Ok'
        except SQLAlchemyError as e: # pragma: nocover
            log.error(u"Error executing %s: %s", query, e)
            raise
        except: # pragma: nocover
            log.exception(u"Unhandled exception executing %s", query)
            raise

        if resultslot is True:
            return result[resultslot]
        else:
            return result

    def filterQueryWithArgs(self, session, conditions, args):
        """Apply filter conditions to the query.

        Should return a `query`, either a SQL statement or an ORM query.
        """

        raise NotImplemented('%s should reimplement this method',
                             self.__class__) # pragma: nocover

    def getColumns(self, query):
        """Return the columns of the given `query`."""

        raise NotImplemented('%s should reimplement this method',
                             self.__class__) # pragma: nocover

    def getCount(self, session, query):
        """Execute a query to get the actual count of matching records."""

        raise NotImplemented('%s should reimplement this method',
                             self.__class__) # pragma: nocover

    def getMetadata(self, session, query, countslot, resultslot, successslot):
        """Description of the result, used to configure an ExtJS store.

        :param session: an SQLAlchemy ``Session``
        :param query: an SQLAlchemy ``Query``
        :param countslot: a string or `None`
        :param resultslot: a string or `None`
        :param successslot: a string or `None`
        :rtype: a dictionary

        For each selected field in the query, this method builds a
        dictionary containing the following keys:

        name
          the name of the field

        type
          the type of the field

        format
          the format of the field, for `date` and `datetime` values

        label
          the localized header for the field

        hint
          a longer description of the field, also localized

        width
          the width of the grid column

        These dictionaries are collected in a list, called ``fields``.

        The information about each field is extracted by two sources:

        1. `self.metadata`, a dictionary keyed on field names: each
           slot may be either a dictionary or a callable accepting the
           field name as parameter and returning the actual dictionary

        2. field column `info`, either a dictionary or a callable
           accepting the field name as parameter and returning the
           actual dictionary

        Also the value of any single slot in the information
        dictionary may be either a scalar value or a callable
        accepting two parameters, the name of the field and the name
        of the slot, returning the actual scalar information, for
        example::

          def birthdate_info(name):
              return {
                  'min': date(1980, 1, 1),
                  'max': lambda fname, iname: date.today()
              }

          persons = Table('persons', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('firstname', String),
                          Column('lastname', String),
                          Column('birthdate', Date, info=birthdate_info),
                         )

        The value coming from proxy `metadata` takes precedence over
        the one from the column `info`.

        Both dictionaries can contain any arbitrary extra slots that
        the caller may use for whatever reason.

        To fulfill ``ExtJS.data.JsonReader`` needs, the resulting
        dictionary contains also the name of the slots used to return
        the *status*, the *result* itself and the total *count* of
        items.

        With the exception of `name`, everything can be overridden
        by `self.metadata`.
        """

        from .json import JSONDateFormat, JSONTimeFormat, JSONTimestampFormat

        fields = []

        satypes_metadata = {
            basestring: dict(type='string'),
            Boolean: dict(type='boolean', width=50),
            Date: dict(type='date', width=85, format=JSONDateFormat),
            DateTime: dict(type='date', width=125, timestamp=True,
                           format=JSONTimestampFormat),
            Integer: dict(type='int', width=60, align='right'),
            Interval: dict(type='string', width=85, align='right',
                           timedelta=True),
            Numeric: dict(type='float', width=70, align='right'),
            String: dict(type='string'),
            Time: dict(type='date', width=85, time=True, format=JSONTimeFormat),
            }

        t = self.translate

        for c in self.getColumns(query):
            meta = dict()
            if isinstance(c, basestring):
                name = c
                cinfo = None
                ctype = basestring
            else:
                name = c.name
                cinfo = getattr(c, 'info', None)
                if cinfo is not None:
                    cinfo = MetaInfo(name, cinfo)
                ctype = c.type
                if hasattr(ctype, 'impl'):
                    ctype = ctype.impl

            fmeta = self.metadata and self.metadata.get(name)

            # An explicit ``False`` means skip the field completely
            if fmeta is False:
                continue

            if fmeta is not None:
                fmeta = MetaInfo(name, fmeta)

            # Explicit order!
            for klass in (String, basestring, Boolean, Numeric, Integer,
                          DateTime, Date, Time, Interval):
                if isinstance(ctype, klass):
                    meta.update(satypes_metadata[klass])
                    break

            if isinstance(ctype, Numeric) and hasattr(ctype, 'scale'):
                meta['decimals'] = ctype.scale

            if isinstance(ctype, Text):
                meta['width'] = 50
            elif isinstance(ctype, String):
                flen = c.type.length
                if flen is None or flen==1:
                    # Flags or SQL expressions like "field || 'suffix'"
                    flen = 10
                meta['width'] = flen*5
                meta['length'] = flen

            if (hasattr(c, 'primary_key') and c.primary_key or
                hasattr(c, 'foreign_keys') and c.foreign_keys):
                meta['hidden'] = True
                meta['readonly'] = True

            if hasattr(c, 'nullable'):
                meta['nullable'] = c.nullable
            else:
                meta['nullable'] = False

            label = fmeta and fmeta.get('label')
            if not label:
                label = cinfo and cinfo.get('label')
            if not label:
                label = name.capitalize()
            else:
                label = t(label)

            hint = fmeta and fmeta.get('hint')
            if not hint:
                hint = cinfo and cinfo.get('hint')
            if not hint:
                hint = ''
            else:
                hint = t(hint)

            # Take info at SA table definition as defaults
            if cinfo is not None:
                meta.update(cinfo)

            # Possibly overridable by metadata
            if fmeta is not None:
                meta.update(fmeta)

            # Override localized strings
            meta['label'] = label
            meta['hint'] = hint
            if 'dictionary' in meta:
                if isinstance(meta['dictionary'], Mapping):
                    meta['dictionary'] = {
                        k: t(v) for k, v in meta['dictionary'].items()}
                else:
                    meta['dictionary'] = [
                        [k, t(v)] for k, v in meta['dictionary']]
            # Do this last, so it cannot be overridden
            meta['name'] = name

            fields.append(meta)

        result = dict(fields=fields)
        if countslot:
            result['count_slot'] = countslot
        if resultslot:
            result['root_slot'] = resultslot
        if successslot:
            result['success_slot'] = successslot

        return result

    def getResult(self, session, query, asdict):
        """Execute the query in the given session, returning the result.

        :param session: an SQLAlchemy ``Session``
        :param query: an SQLAlchemy ``Query``
        :param asdict: a boolean

        If `asdict` is False then this should return either a
        ``ResultSet`` (for SQL selects) or a list of entities (when
        the query is at the ORM level), otherwise they should be
        translated into a list of dictionaries.
        """

        raise NotImplemented('%s should reimplement this method',
                             self.__class__) # pragma: nocover


class ProxiedEntity(ProxiedBase):
    """Facility class to expose a SQLAlchemy entity to Pylons.

    An instance of this class wraps an *entity*, that is a SQLAlchemy
    mapped class. When called it builds a query, eventually applying
    filters specified by the arguments and returning the results set.

    This is somewhat less efficient than ``ProxiedQuery``, as it uses
    the ``ORM`` layer.
    """

    def __init__(self, entity, fields=None, metadata=None):
        """Initialize the proxy.

        :param entity: a SQLAlchemy mapped class, or an ORM query
        :param fields: a list of field names
        :param metadata: a dictionary

        When `fields` is not specified, it is automatically computed
        from the list of columns of the mapped table, extended with
        the properties defined on the entity itself.

        `metadata` is a dictionary, containing extra information
        about fields: when possibile, these info are collected from
        the SA definition (each field has a `info` dictionary); for
        computed fields when the returned value does not correspond to
        a physical field, or simply to override/expand such
        information on a per query basis, you may pass an additional
        dictionary of values, keyed on the field name.
        """

        super(ProxiedEntity, self).__init__()

        if isinstance(entity, Query):
            self.query = entity
            self.entity = entity._entity_zero().entity_zero.entity
        else:
            self.query = None
            self.entity = entity

        if fields is None:
            fields = [prop.key
                      for prop in class_mapper(self.entity).iterate_properties
                      if isinstance(prop, ColumnProperty)]
            fields.extend([a for a in dir(self.entity)
                           if (not a.startswith('_')
                               and isinstance(getattr(self.entity, a), property)
                               and a not in fields)])
        self.fields = fields
        self.metadata = metadata

    def filterQueryWithArgs(self, session, conditions, args):
        """Construct a filtered query on the wrapper entity.

        The query gets then massaged by `apply_filters()`, further
        filtered and modified as specified by the `args` dictionary.

        Return the altered query.
        """

        if self.query is None:
            query = session.query(self.entity)
        else:
            query = self.query
            query.session = session

        if conditions:
            if len(conditions)>1:
                query = query.filter(and_(conditions))
            else:
                query = query.filter(conditions[0])

        query, self.only_cols = apply_filters(query, args)
        return query

    def getColumns(self, query):
        """Return the columns specified by `self.fields`."""

        stmt = query.statement
        oc = self.only_cols
        columns = []
        for n in self.fields:
            if oc is None or n in oc:
                col = col_by_name(stmt, n)
                if col is None:
                    col = n
                columns.append(col)
        return columns

    def getCount(self, session, query):
        """Execute a query to get the actual count of matching records."""

        return query.count()

    def getResult(self, session, query, asdict):
        """Execute the query in the given session, returning the result."""

        result = query.all()
        if asdict:
            oc = self.only_cols
            result = [dict((f, getattr(o, f))
                           for f in self.fields
                           if oc is None or f in oc)
                      for o in result]
        return result

    def getMetadata(self, session, query, countslot, resultslot, successslot):
        """Augment superclass implementation with primary key name."""

        result = super(ProxiedEntity, self).getMetadata(session, query,
                                                        countslot, resultslot,
                                                        successslot)

        pk = class_mapper(self.entity).primary_key
        if len(pk) == 1:
            result['primary_key'] = pk[0].name
        else:
            result['primary_key'] = [c.name for c in pk]

        return result


class ProxiedQuery(ProxiedBase):
    """Facility class to expose a SQLAlchemy statement to Pylons.

    An instance of this class wraps a standard SQLAlchemy query,
    either a selectable or an updateable. When called it applies the
    arguments filtering or changing the original query, calling it
    and returning the results set.
    """

    def __init__(self, query, metadata=None):
        """Initialize the proxy.

        `query` is the basic SA statement, either a ``SELECT`` or any
        *DML* statement (although only the first kind is currently
        supported!).

        `metadata` is a dictionary, containing extra information
        about fields: when possibile, these info are collected from
        the SA definition (each field has a `info` dictionary); for
        computed fields when the returned value does not correspond to
        a physical field, or simply to override/expand such
        information on a per query basis, you may pass an additional
        dictionary of values, keyed on the field name.
        """

        super(ProxiedQuery, self).__init__()

        self.query = query
        self.metadata = metadata

    def __str__(self):
        return str(self.query)

    def filterQueryWithArgs(self, session, conditions, args):
        """Apply filter conditions to the query.

        `conditions`, if specified, is a list of SQLAlchemy
        expressions to be applied as filters to the query, using
        the ``AND`` operator.

        The query gets then massaged by `apply_filters()`, further
        filtered and modified as specified by the `args` dictionary.

        Return the altered query.
        """

        if conditions:
            if len(conditions)>1:
                query = self.query.where(and_(conditions))
            else:
                query = self.query.where(conditions[0])
        else:
            query = self.query
        query, only_cols = apply_filters(query, args)

        values = self.params = {}
        params = args.pop('params', None)
        if params is not None:
            from sqlalchemy.sql.visitors import traverse

            # Extract the eventual bindparams from the query and
            # adapt each argument value to the declared type.
            def adapt_args(bind):
                if bind.key in params and bind.key not in values:
                    coerce_value = get_adaptor_for_type(bind.type)
                    values[bind.key] = coerce_value(params[bind.key])
            traverse(query, {},  {'bindparam': adapt_args})

        return query

    def getColumns(self, query):
        """Return the selected columns."""

        return query.inner_columns

    def getCount(self, session, query):
        """Execute a query to get the actual count of matching records."""

        pivot = next(query.inner_columns)
        simple = query.with_only_columns([pivot])
        tquery = select([func.count()], from_obj=simple.alias('cnt'))
        return session.execute(tquery, self.params).scalar()

    def getResult(self, session, query, asdict):
        """Execute the query in the given session, returning the result.

        If `asdict` is `True` return a list of dictionaries, one for
        each row, otherwise return the SQLAlchemy resultset (as
        returned by ``.fetchall()``).
        """

        # XXX: this does not currently handle SA Updateables!

        if isinstance(query, Selectable):
            result = session.execute(query, self.params)
            if asdict:
                result = [dict(r) for r in result]
            else:
                result = result.fetchall()
        else:
            result = None
        return result

    def getMetadata(self, session, query, countslot, resultslot, successslot):
        """Augment superclass implementation with primary key name.

        Beware, this implements a rather simplicistic heuristic such that it
        identifies only the primary key of the first table involved in the
        query: in other words, it assumes that the primary key fields come
        as early as possible in the list of columns.
        """

        result = super(ProxiedQuery, self).getMetadata(session, query,
                                                       countslot, resultslot,
                                                       successslot)

        pk = []
        pkt = None
        pkl = 0
        for c in self.getColumns(query):
            if hasattr(c, 'table') and getattr(c, 'primary_key', False):
                if pkt is None:
                    pkt = c.table
                    pkl = len(pkt.primary_key)
                if c.table is pkt:
                    pk.append(c)
                    if len(pk) == pkl:
                        break

        if pk and pkl == len(pk):
            if len(pk) == 1:
                result['primary_key'] = pk[0].name
            else:
                result['primary_key'] = [c.name for c in pk]
        else:
            log.warning(u"Could not determine primary key fields"
                        u" for query %s", query)

        return result


def create_change_saver(adaptor=None, save_changes=None,
                        modified_slot_name='modified_records',
                        deleted_slot_name='deleted_records',
                        inserted_ids_slot='inserted_ids',
                        modified_ids_slot='modified_ids',
                        deleted_ids_slot='deleted_ids',
                        result_slot='root',
                        success_slot='success',
                        message_slot='message'):
    """Function factory to implement the standard POST handler for a proxy.

    :param adaptor: a function that adapts the changes before application
    :param save_changes: the function that concretely applies the changes
    :param modified_slot_name: a string, by default 'modified_records'
    :param deleted_slot_name: a string, by default 'deleted_records'
    :param inserted_ids_slot: a string, by default 'inserted_ids'
    :param modified_ids_slot: a string, by default 'modified_ids'
    :param deleted_ids_slot: a string, by default 'deleted_ids'
    :param result_slot: a string, by default 'root'
    :param success_slot: a string, by default 'success'
    :param message_slot: a string, by default 'message'
    :returns: a dictionary, with a boolean `success` slot with a
        ``True`` value if the operation was completed without errors,
        ``False`` otherwise: in the latter case the `message` slot
        contains the reason for the failure. Three other slots carry
        lists of dictionaries with the ids of the *inserted*,
        *modified* and *deleted* records.

    This implements the generic behaviour we need to save changes back to
    the database.

    The `adaptor` function takes four arguments, respectively the SA
    session, the request, a list of added/modified records and a list
    of deleted records; it must return two (possibly modified) lists,
    one containing added/modified records and the other with the
    records to delete, e.g.::

        def adaptor(sa_session, request, modified_recs, deleted_recs):
            # do any step to adapt incoming data
            return modified_recs, deleted_recs
    """

    def workhorse(sa_session, request, **args):
        from .json import json2py

        mr = json2py(args[modified_slot_name])
        dr = json2py(args[deleted_slot_name])

        if adaptor is not None:
            try:
                mr, dr = adaptor(sa_session, request, mr, dr)
            except Exception as e:
                log.critical(u'Could not adapt changes: %s', e, exc_info=True)
                return {
                    success_slot: False,
                    message_slot: u'Internal error, consult application log'
                }

        try:
            iids, mids, dids = save_changes(sa_session, request, mr, dr)
            status = True
            statusmsg = "Ok"
        except SQLAlchemyError as e:
            msg = get_exception_message(e)
            log.error(u'Could not save changes to the database: %s', msg)
            status = False
            statusmsg = msg.split('\n')[0]
            iids = mids = dids = None
        except Exception as e:
            msg = get_exception_message(e)
            log.critical(u'Could not save changes to the database: %s',
                         msg, exc_info=True)
            status = False
            statusmsg = u'Internal error, consult application log.'
            iids = mids = dids = None

        return { success_slot: status,
                 message_slot: statusmsg,
                 inserted_ids_slot: iids,
                 modified_ids_slot: mids,
                 deleted_ids_slot: dids,
               }

    return workhorse
