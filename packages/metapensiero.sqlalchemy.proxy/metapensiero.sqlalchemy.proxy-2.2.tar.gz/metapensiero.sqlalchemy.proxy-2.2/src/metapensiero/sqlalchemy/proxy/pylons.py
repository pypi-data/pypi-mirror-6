# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.sqlalchemy.proxy -- Pylons decorator glue
# :Creato:    mar 28 apr 2009 23:37:24 CEST
# :Autore:    Lele Gaifax <lele@nautilus.homeip.net>
# :Licenza:   GNU General Public License version 3 or later
#

from __future__ import absolute_import

import logging

from decorator import decorator
from pylons import request, response
from webob.exc import HTTPInternalServerError

from .json import py2json
from . import formatter

log = logging.getLogger(__name__)


# Syntactic sugar decorator: implements the default policy of calling
# a proxied thingie.
def proxy(fget, fpost=None, fdel=None,
          result='root', count='count', success='success',
          default_format='json'):
    """Execute the proxied thing, forwarding given arguments.

    :param fget: either a ``ProxiedQuery`` or a ``ProxiedEntity`` instance
    :param fpost: eventual ``POST`` functionality
    :param fdel: eventual ``DEL`` functionality
    :param result: a string or a boolean
    :param count: a string or a boolean
    :param format: a string or a boolean
    :rtype: the wrapped proxy

    This calls the proxy `fget`, forwarding positional and keyword
    arguments, with the exception of ``sa_session``: this indicate the
    SQLAlchemy session to use, if `None` (default) a new session is
    created, using ``self.sa_session``. If `fpost` or `fdel` are
    specified, then the request method (that is, ``GET``, ``POST`` or
    ``DEL``) will be used to select the function to call. In any case,
    the function should be a callable receiving at least one positional
    arguments, the SQLAlchemy session.

    When no keyword argument is specified, those coming from the
    ``REQUEST`` are used instead. This make it easier doing cross
    calls between different proxied things.

    `result`, `count` and `format`, if not specified at call time as
    keyword arguments, will be used as default values for the homonym
    keyword.

    The usage is as follow::

      class MyController(Controller):
          _query = ProxiedQuery(select([table]))
          "The basic SQLalchemy query."

          query = proxy(_query)
          "The query, returning a JSON dataset."

          queryCount = proxy(_query, result=None)
          "Return only a count of resulting rows."

          queryNative = proxy(_query, result=True)
          "Return the native datasets."

          def _adaptor(sess, req, modrecs, delrecs):
              # do any step to adapt incoming data
              return modrecs, delrecs

          readAndWrite = proxy(
              _query, create_change_saver(_adaptor, save_changes=save_changes))
          "Implement both a GET and a POST handler"
    """

    def new_f(self, sa_session=None, *conditions, **args):
        # if we have no kwargs or we are in a pylons context, use
        # the arguments coming from the request
        if not args or 'pylons' in args:
            args = request.params.mixed()
        if 'result' not in args:
            args['result'] = result
        if 'count' not in args:
            args['count'] = count
        if 'success' not in args:
            args['success'] = count

        format = args.get('format', default_format)
        formatter = PylonsFormatter.bind(format)

        if format == 'json':
            args['asdict'] = True

        if sa_session is None:
            sa_session = self.sa_session

        try:
            if request.method == 'GET' or fpost is fdel is None:
                res = formatter(fget, *conditions, **args)(sa_session)
            elif request.method == 'POST' and fpost is not None:
                res = fpost(sa_session, request, **args)
            elif request.method == 'DEL' and fdel is not None:
                res = fdel(sa_session, request,  **args)
            return res
        except BaseException as e:
            log.exception(u'Proxy execution failed')
            raise HTTPInternalServerError(u'Proxy execution failed: %s' % e)

        log.error(u'Unrecognized method: %s' % request.method)
        raise ValueError(u'Unrecognized method: %s' % request.method)

    new_f.__dict__ = fget.__dict__
    return new_f


@decorator
def jsonify(func, *args, **kwargs):
    """Action decorator that formats output for JSON

    Given a function returning some value, this decorator wraps it
    converting the result in JSON, with a content-type of
    'text/javascript' and output it.

    This is usually used in this way::

      class MyController(Controller):
          @jsonify
          def sayHello(self):
              return 'Hello!'
    """

    response.headers['Content-Type'] = 'text/javascript'
    data = func(*args, **kwargs)
    return py2json(data)


class PylonsFormatter(formatter.BaseFormatter):

    filename = None
    mimetype = 'text/plain'

    def __call__(self, session):
        response.content_type = self.mimetype
        if self.filename:
            response.headers['Content-Disposition'] = 'attachment;filename=%s' % self.filename
        return super(PylonsFormatter, self).__call__(session)


class JSONFormatter(PylonsFormatter):

    mimetype = 'text/javascript'

    def __call__(self, session):
        data = super(JSONFormatter, self).__call__(session)
        return py2json(data)

JSONFormatter.register('json')
