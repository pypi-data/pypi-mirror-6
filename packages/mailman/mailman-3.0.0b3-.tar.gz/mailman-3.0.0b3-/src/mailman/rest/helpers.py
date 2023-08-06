# Copyright (C) 2010-2014 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

"""Web service helpers."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'GetterSetter',
    'PATCH',
    'etag',
    'no_content',
    'path_to',
    'restish_matcher',
    ]


import cgi
import json
import hashlib

from cStringIO import StringIO
from datetime import datetime, timedelta
from enum import Enum
from lazr.config import as_boolean
from restish import http
from restish.http import Response
from restish.resource import MethodDecorator
from webob.multidict import MultiDict

from mailman.config import config



def path_to(resource):
    """Return the url path to a resource.

    :param resource: The canonical path to the resource, relative to the
        system base URI.
    :type resource: string
    :return: The full path to the resource.
    :rtype: bytes
    """
    return b'{0}://{1}:{2}/{3}/{4}'.format(
        ('https' if as_boolean(config.webservice.use_https) else 'http'),
        config.webservice.hostname,
        config.webservice.port,
        config.webservice.api_version,
        (resource[1:] if resource.startswith('/') else resource),
        )



class ExtendedEncoder(json.JSONEncoder):
    """An extended JSON encoder which knows about other data types."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            # as_timedelta() does not recognize microseconds, so convert these
            # to floating seconds, but only if there are any seconds.
            if obj.seconds > 0 or obj.microseconds > 0:
                seconds = obj.seconds + obj.microseconds / 1000000.0
                return '{0}d{1}s'.format(obj.days, seconds)
            return '{0}d'.format(obj.days)
        elif isinstance(obj, Enum):
            # It's up to the decoding validator to associate this name with
            # the right Enum class.
            return obj.name
        return json.JSONEncoder.default(self, obj)


def etag(resource):
    """Calculate the etag and return a JSON representation.

    The input is a dictionary representing the resource.  This dictionary must
    not contain an `http_etag` key.  This function calculates the etag by
    using the sha1 hexdigest of the repr of the dictionary.  It then inserts
    this value under the `http_etag` key, and returns the JSON representation
    of the modified dictionary.

    :param resource: The original resource representation.
    :type resource: dictionary
    :return: JSON representation of the modified dictionary.
    :rtype string
    """
    assert 'http_etag' not in resource, 'Resource already etagged'
    etag = hashlib.sha1(repr(resource)).hexdigest()

    resource['http_etag'] = '"{0}"'.format(etag)
    return json.dumps(resource, cls=ExtendedEncoder)


def paginate(method):
    """Method decorator to paginate through collection result lists.

    Use this to return only a slice of a collection, specified in the request
    itself.  The request should use query parameters `count` and `page` to
    specify the slice they want.  The slice will start at index
    ``(page - 1) * count`` and end (exclusive) at ``(page * count)``.

    Decorated methods must take ``self`` and ``request`` as the first two
    arguments.
    """
    def wrapper(self, request, *args, **kwargs):
        try:
            count = int(request.GET['count'])
            page = int(request.GET['page'])
            if count < 0 or page < 0:
                return http.bad_request([], b'Invalid parameters')
        # Wrong parameter types or no GET attribute in request object.
        except (AttributeError, ValueError, TypeError):
            return http.bad_request([], b'Invalid parameters')
        # No count/page params.
        except KeyError:
            count = page = None
        result = method(self, request, *args, **kwargs)
        if count is None and page is None:
            return result
        list_start = int((page - 1) * count)
        list_end = int(page * count)
        return result[list_start:list_end]
    return wrapper



class CollectionMixin:
    """Mixin class for common collection-ish things."""

    def _resource_as_dict(self, resource):
        """Return the dictionary representation of a resource.

        This must be implemented by subclasses.

        :param resource: The resource object.
        :type resource: object
        :return: The representation of the resource.
        :rtype: dict
        """
        raise NotImplementedError

    def _resource_as_json(self, resource):
        """Return the JSON formatted representation of the resource."""
        return etag(self._resource_as_dict(resource))

    def _get_collection(self, request):
        """Return the collection as a concrete list.

        This must be implemented by subclasses.

        :param request: A restish request.
        :return: The collection
        :rtype: list
        """
        raise NotImplementedError

    def _make_collection(self, request):
        """Provide the collection to restish."""
        collection = self._get_collection(request)
        if len(collection) == 0:
            return dict(start=0, total_size=0)
        else:
            entries = [self._resource_as_dict(resource)
                       for resource in collection]
            # Tag the resources but use the dictionaries.
            [etag(resource) for resource in entries]
            # Create the collection resource
            return dict(
                start=0,
                total_size=len(collection),
                entries=entries,
                )



# XXX 2010-02-24 barry Seems like contrary to the documentation, matchers
# cannot be plain functions, because matchers must have a .score attribute.
# OTOH, I think they support regexps, so that might be a better way to go.
def restish_matcher(function):
    """Decorator for restish matchers."""
    function.score = ()
    return function


# restish doesn't support HTTP response code 204.
def no_content():
    """204 No Content."""
    return Response('204 No Content', [], None)


# These two classes implement an ugly, dirty hack to work around the fact that
# neither WebOb nor really the stdlib cgi module support non-standard HTTP
# verbs such as PATCH.  Note that restish handles it just fine in the sense
# that the right method gets called, but without the following kludge, the
# body of the request will never get decoded, so the method won't see any
# data.
#
# Stuffing the MultiDict on request.PATCH is pretty ugly, but it mirrors
# WebOb's use of request.POST and request.PUT for those standard verbs.
# Besides, WebOb refuses to allow us to set request.POST.  This does make
# validators.py a bit more complicated. :(

class PATCHWrapper:
    """Hack to decode the request body for PATCH."""
    def __init__(self, func):
        self.func = func

    def __call__(self, resource, request):
        # We can't use request.body_file because that's a socket that's
        # already had its data read off of.  IOW, if we use that directly,
        # we'll block here.
        field_storage = cgi.FieldStorage(
            fp=StringIO(request.body),
            # Yes, lie about the method so cgi will do the right thing.
            environ=dict(REQUEST_METHOD='POST'),
            keep_blank_values=True)
        request.PATCH = MultiDict.from_fieldstorage(field_storage)
        return self.func(resource, request)


class PATCH(MethodDecorator):
    method = 'PATCH'

    def __call__(self, func):
        really_wrapped_func = PATCHWrapper(func)
        return super(PATCH, self).__call__(really_wrapped_func)


class GetterSetter:
    """Get and set attributes on an object.

    Most attributes are fairly simple - a getattr() or setattr() on the object
    does the trick, with the appropriate encoding or decoding on the way in
    and out.  Encoding doesn't happen here though; the standard JSON library
    handles most types, but see ExtendedEncoder for additional support.

    Others are more complicated since they aren't kept in the model as direct
    columns in the database.  These will use subclasses of this base class.
    Read-only attributes will have a decoder which always raises ValueError.
    """

    def __init__(self, decoder=None):
        """Create a getter/setter for a specific attribute.

        :param decoder: The callable for decoding a web request value string
            into the specific data type needed by the object's attribute.  Use
            None to indicate a read-only attribute.  The callable should raise
            ValueError when the web request value cannot be converted.
        :type decoder: callable
        """
        self.decoder = decoder

    def get(self, obj, attribute):
        """Return the named object attribute value.

        :param obj: The object to access.
        :type obj: object
        :param attribute: The attribute name.
        :type attribute: string
        :return: The attribute value, ready for JSON encoding.
        :rtype: object
        """
        return getattr(obj, attribute)

    def put(self, obj, attribute, value):
        """Set the named object attribute value.

        :param obj: The object to change.
        :type obj: object
        :param attribute: The attribute name.
        :type attribute: string
        :param value: The new value for the attribute.
        """
        setattr(obj, attribute, value)

    def __call__(self, value):
        """Convert the value to its internal format.

        :param value: The web request value to convert.
        :type value: string
        :return: The converted value.
        :rtype: object
        """
        if self.decoder is None:
            return value
        return self.decoder(value)
