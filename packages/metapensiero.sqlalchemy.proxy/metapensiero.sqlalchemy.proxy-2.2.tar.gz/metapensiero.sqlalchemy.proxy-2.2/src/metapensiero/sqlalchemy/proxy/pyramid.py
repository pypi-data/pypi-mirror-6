# -*- coding: utf-8 -*-
#:Progetto:  metapensiero.sqlalchemy.proxy -- Pyramid decorator glue
#:Creato:    mer 08 ago 2012 19:07:28 CEST
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

"""Install a custom JSON renderer, able to deal with datetimes.

This is usually installed by including this module from the
configuration file, for example::

  pyramid.includes =
    metapensiero.sqlalchemy.proxy.pyramid
"""

from __future__ import absolute_import

from collections import Callable
from functools import wraps
from inspect import isgeneratorfunction

from pyramid.i18n import get_localizer
from sqlalchemy.sql.expression import Select

import transaction

from . import (
    ProxiedBase,
    ProxiedEntity as PEBase,
    ProxiedQuery as PQBase,
    create_change_saver,
    )


class ProxiedEntity(PEBase):
    def __call__(self, session, request, *conditions, **args):
        self.translate = get_localizer(request).translate
        if not 'result' in args:
            args['result'] = 'root'
        if not 'count' in args:
            args['count'] = 'count'
        if not 'success' in args:
            args['success'] = 'success'
        return super(ProxiedEntity, self).__call__(session, *conditions, **args)


class ProxiedQuery(PQBase):
    def __call__(self, session, request, *conditions, **args):
        self.translate = get_localizer(request).translate
        if not 'result' in args:
            args['result'] = 'root'
        if not 'count' in args:
            args['count'] = 'count'
        if not 'success' in args:
            args['success'] = 'success'
        return super(ProxiedQuery, self).__call__(session, *conditions, **args)


class expose(object):
    """Decorator to simplify exposition of a SQLAlchemy Query.

    This is an helper class that aids the exposition of either a SQLAlchemy
    Query or directly a mapped class as a Pyramid view.

    User of this class **must** inject a concrete implementation of the
    :py:meth:`create_session` and :py:meth:`save_changes` static
    methods. This is usually done once at application startup, for
    example::

        from ..models import DBSession
        from ..models.utils import save_changes

        # Configure the `expose` decorator
        expose.create_session = staticmethod(lambda req: DBSession())
        expose.save_changes = staticmethod(save_changes)

    Another *class* method that may eventually be replaced is
    :py:method:`extract_parameters`: the default implementation simply
    returns a copy of the `request.params` dictionary, but sometimes
    it is desiderable to pass additional parameters, for example when
    using `bindparams`::

        def _extract_parameters(request):
            "Build a dictionary of arguments for the proxy from the current request"

            parameters = dict(request.params)
            # The following feeds eventual `bindparams`
            parameters['params'] = dict(request.session)
            return parameters

        expose.extract_parameters = staticmethod(_extract_parameters)

    The typical usage is::

        @view_config(route_name='users', renderer='json')
        @expose(User, metadata=dict(
            password=dict(hidden=True, password=True, width=40),
            is_anonymous=False,
            ))
        def users(request, results):
            return results

    The first argument may be either a mapped class or a query.

    The decorated function is finally called with the current request
    and the result of the operation, and it can eventually adjust the
    `results` dictionary.

    The decorated function may be a generator instead, which has the
    opportunity of freely manipulate either the arguments received
    from the request, or the final result, or both as follows::

        @expose(User, metadata=dict(
            password=dict(hidden=True, password=True, width=40),
            is_anonymous=False,
            ))
        def complex():
            # Receive request and params
            request, params = (yield)
            log.debug('REQUEST: %r', request)

            # Adjust parameters
            params['new'] = True

            if 'something' in params:
                # Inject other conditions
                something = params.pop('something')
                conditions = (User.c.foo == something,)
                result = yield params, conditions
            else:
                # Go on, and receive the final result
                result = yield params

            # Fix it up
            result['COMPLEX'] = 'MAYBE'

            yield result

    As you can see, in this case the decorated function shall not
    declare any formal argument, because it receives its "feed" as the
    result of the ``yield`` expressions.
    """

    @staticmethod
    def create_session(request):
        """Create a new SQLAlchemy session, given the current request."""

        raise NotImplementedError

    @staticmethod
    def extract_parameters(request):
        """Create a dictionary of parameters from the current request."""

        return dict(request.params)

    @staticmethod
    def save_changes(sa_session, modified, deleted):
        """Save insertions, changes and deletions to the database.

        :param sa_session: the SQLAlchemy session
        :param modified: a sequence of record changes, each represented by
            a tuple of two items, the PK name and a
            dictionary with the modified fields; if the value
            of the PK field is null or 0 then the record is
            considered new and will be inserted instead of updated
        :param deleted: a sequence of deletions, each represented by a tuple
            of two items, the PK name and the ID of the record to
            be removed
        :rtype: a tuple of three lists, respectively inserted, modified and
            deleted record IDs, grouped in a dictionary keyed on PK name.
        """

        raise NotImplementedError

    def __init__(self, proxable, metadata=None, adaptor=None, POST=True, **kw):
        """Initialize the decorator.

        :param proxable: either a SQLAlchemy Query or a mapped class
        :param metadata: a dictionary with additional info about the fields
        :param adaptor: if given, it's a function that will be called to adapt
           incoming data before actually writing it to the database.
        :type POST: either a boolean flag or a function, ``True`` by default
        :keyword POST: whether to handle POST request: if ``True`` a standard
           function will be used, otherwise it must be a function accepting two
           positional arguments, respectively the SQLAlchemy session and the
           Pyramid request object, and a set of keyword arguments corresponding
           to the changed field
        """

        if isinstance(proxable, ProxiedBase):
            self.proxy = proxable
        elif isinstance(proxable, Select):
            self.proxie = ProxiedQuery(proxable, metadata=metadata)
        else:
            self.proxie = ProxiedEntity(proxable, metadata=metadata,
                                        fields=kw.get('fields'))
        if POST:
            if POST is True:
                POST = create_change_saver(adaptor, self.save_changes)
            elif not isinstance(POST, Callable):
                raise ValueError(
                    'POST parameter must be either a boolean or a function,'
                    ' got a %r' % type(POST))
            self.POST = POST
        else:
            self.POST = None
        for method in kw:
            if method.isupper():
                handler = kw[method]
                if isinstance(handler, Callable):
                    setattr(self, method, handler)
                else:
                    raise ValueError(
                        '%s parameter must be either a boolean or a function,'
                        ' got a %r' % (method, type(handler)))

    def __call__(self, method):
        @wraps(method)
        def workhorse(request):
            adapt = method().send if isgeneratorfunction(method) else False

            sa_session = self.create_session(request)
            params = self.extract_parameters(request)
            conditions = ()

            with transaction.manager:
                if adapt:
                    adapt(None)
                    params = adapt((request, params))
                    if isinstance(params, tuple):
                        params, conditions = params

                if request.method == 'GET':
                    result = self.proxie(sa_session, request, *conditions,
                                         asdict=True, **params)
                else:
                    handler = getattr(self, request.method, None)
                    if handler is None:
                        raise NotImplemented(
                            'Could not handle %s request' % request.method)
                    result = handler(sa_session, request, **params)

                if adapt:
                    result = adapt(result)
                else:
                    result = method(request, result)

                return result

        return workhorse


def json_renderer_factory(info):
    from .json import py2json

    def _render(value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'application/json'
        return py2json(value)
    return _render


def includeme(config):
    """Install our JSON renderer, able to deal with datetimes."""

    config.add_renderer('json', json_renderer_factory)
