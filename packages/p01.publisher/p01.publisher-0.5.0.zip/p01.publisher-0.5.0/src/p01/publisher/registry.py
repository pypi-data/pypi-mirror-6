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
"""Publisher registry

$Id: registry.py 3903 2013-12-20 03:45:39Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.publisher.interfaces import ISkinnable
from zope.publisher.skinnable import setDefaultSkin
from zope.configuration.exceptions import ConfigurationError

from p01.publisher import interfaces


@zope.interface.implementer(interfaces.IPublisherRegistry)
class PublisherRegistry(object):
    """The registry implements a three stage lookup for registered factories
    that have to deal with requests::

      {method > { mimetype -> [{'priority' : some_int,
                                 'factory' :  factory,
                                 'name' : some_name }, ...
                                ]
                  },
      }

    The `priority` is used to define a lookup-order when multiple factories
    are registered for the same method and mime-type.
    """

    def __init__(self):
        self._d = {}   # method -> { mimetype -> {factories_data}}

    def register(self, method, mimetype, name, priority, factory):
        """Register a factory for method+mimetype """

        # initialize the two-level deep nested datastructure if necessary
        if not self._d.has_key(method):
            self._d[method] = {}
        if not self._d[method].has_key(mimetype):
            self._d[method][mimetype] = []
        l = self._d[method][mimetype]

        # Check if there is already a registered publisher factory (check by
        # name).  If yes then it will be removed and replaced by a new
        # publisher.
        for pos, d in enumerate(l):
            if d['name'] == name:
                del l[pos]
                break
        # add the publisher factory + additional informations
        l.append({'name' : name, 'factory' : factory, 'priority' : priority})

        # order by descending priority
        l.sort(lambda x,y: -cmp(x['priority'], y['priority']))

        # check if the priorities are unique
        priorities = [item['priority'] for item in l]
        if len(set(priorities)) != len(l):
            raise ConfigurationError('All registered publishers for a given '
                                     'method+mimetype must have distinct '
                                     'priorities. Please check your ZCML '
                                     'configuration')

    def getFactoriesFor(self, method, mimetype):
        if ';' in mimetype:
            # `mimetype` might be something like 'text/xml; charset=utf8'. In
            # this case we are only interested in the first part.
            mimetype = mimetype.split(';')[0]
        try:
            return self._d[method][mimetype.strip()]
        except KeyError:
            return None

    def lookup(self, method, mimetype, environment):
        """Lookup a factory for a given method+mimetype and a environment."""
        for m,mt in ((method, mimetype), (method, '*'), ('*', '*')):
            factory_lst = self.getFactoriesFor(m, mt)
            if factory_lst:
                break
        else:
            raise ConfigurationError('No registered publisher found '
                                     'for (%s/%s)' % (method, mimetype))

        # now iterate over all factory candidates and let them introspect
        # the request environment to figure out if they can handle the
        # request
        for d in factory_lst:
            return d['factory']

        # Actually we should never get here unless of improper
        # configuration (no default handler for method=* and mimetype=*)
        return None


registry = PublisherRegistry()


def chooseClasses(method, environment):
    """Choose request and publication classes
    
    Given the method and environment, choose the correct request and
    publication classes
    """
    content_type = environment.get('CONTENT_TYPE', '')
    factory = registry.lookup(method, content_type, environment)
    request_class, publication = factory()
    return request_class, publication


try:
    import zope.testing.cleanup
except ImportError:
    pass
else:
    zope.testing.cleanup.addCleanUp(lambda : registry.__init__())
