##############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Publisher

$Id: publisher.py 3916 2014-01-02 04:21:45Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import sys

import zope.component
from zope.publisher.interfaces import Retry
from zope.publisher.interfaces import IReRaiseException
from zope.publisher.interfaces import ISkinnable
from zope.publisher.skinnable import setDefaultSkin

from p01.publisher import interfaces
from p01.publisher.registry import chooseClasses


def debug_call(obj, args):
    # The presence of this function allows us to set a pdb breakpoint
    return obj(*args)


def publish(request, handle_errors=True):
    """Publish stack, see IPublisher for details
    
    The precence of this method allows to use the publis stack without
    a publisher. This is usefull for testing and debugging.
    """
    try:
        # finally to clean up to_raise and close request
        to_raise = None
        # get publication
        obj = None
        publication = request.publication
        try:
            # start transaction
            publication.startRequest(request)
            # process input stream
            request.processInputs()
            # notify traversal start
            publication.beforeTraversal(request)
            # get application
            obj = publication.getApplication(request)
            # traverse
            obj = request.traverse(obj)
            # process object (page)
            result = publication.callObject(request, obj)
            # get response and result
            response = request.response
            if result is not response:
                response.setResult(result)
            # notify after call
            publication.afterCall(request, obj)
        except:
            # handle publication error
            exc_info = sys.exc_info()
            try:
                publication.handleException(obj, request, exc_info)
            except:
                # bad exception handler handling exception, make sure this
                # never happens! But if so make sure internalError method
                # knows whats to do
                request.response.internalError()
                to_raise = sys.exc_info()
            if not handle_errors:
                # wsgi.handle_error = True means the zope publisher
                # should handle errors and don't dispatch them to
                # wsgi. In case zope should not handle error just
                # raise it here. This is only used for testing
                raise
        finally:
            publication.endRequest(request, obj)

        response = request.response
        if to_raise is not None:
            # raise not catched exceptions
            raise to_raise[0], to_raise[1], to_raise[2]

    finally:
        # avoid circ. ref.
        to_raise = None
        # close request and cleanup hooks in request._held
        request.close()

    # return the request
    return request


@zope.interface.implementer(interfaces.IPublisher)
class Publisher(object):
    """Publisher shared per wsgi application
    
    A Publisher knows how to get the right request class based on a given
    environment. The publisher is also responible for setup the right skin.
    """

    def __init__(self, app, handle_errors=False):
        self._app = app
        self._handle_errors = handle_errors
        self._cache = {}

    def __call__(self, input_stream, env):
        """Lookup request and publication class based on given request"""
        method = env.get('REQUEST_METHOD', 'GET').upper()
        request_class, publication_class = chooseClasses(method, env)

        # get publication (singleton per request type)
        publication = self._cache.get(publication_class)
        if publication is None:
            publication = publication_class(self._app)
            self._cache[publication_class] = publication

        # setup request
        request = request_class(input_stream, env)
        request.setPublication(publication)
        if ISkinnable.providedBy(request):
            # only ISkinnable requests have skins
            setDefaultSkin(request)
        return request

    def publish(self, request, handle_errors=None):
        # use handle_errors if not None or default (self._handle_errors)
        return publish(request, handle_errors or self._handle_errors)
