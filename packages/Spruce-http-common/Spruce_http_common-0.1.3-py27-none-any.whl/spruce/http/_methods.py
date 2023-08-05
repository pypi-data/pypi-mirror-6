"""Request methods."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"


def method_defines_body_semantics(method):
    """
    Whether an HTTP method defines semantics for handling the body of a
    request message entity.

    The :rfc:`HTTP/1.1 methods specification <2616#section-9>` declares some
    HTTP methods as assigning an interpretation to the entity body in a
    request message.  This function determines whether the given *method*
    belongs to this category.

    The :rfc:`HTTP/1.1 message body specification <2616#section-4.3>`
    recommends certain server behaviors on this basis:

        A server SHOULD read and forward a message-body on any request; if
        the request method does not include defined semantics for an
        entity-body, then the message-body SHOULD be ignored when handling
        the request.

    """
    return method in ('OPTIONS', 'PATCH', 'POST', 'PUT')


def method_disallows_body(method):
    """
    Whether an HTTP method disallows its request messages to have entity
    bodies.

    The :rfc:`HTTP/1.1 message body specification <2616#section-4.3>`
    requires certain client behavior on this basis:

        A message-body MUST NOT be included in a request if the
        specification of the request method (section 5.1.1) does not allow
        sending an entity-body in requests.

    .. note::
        The :rfc:`HTTP/1.1 methods specification <2616#section-9>` does not
        define semantics for entity bodies in the request messages for some
        methods.  But none of the methods actually disallow entity bodies,
        so this function always returns :obj:`False`.  However, this is
        subject to change with future HTTP revisions and extensions, so this
        function should still be used where applicable.

    """
    return False


METHODS = ('CONNECT', 'DELETE', 'HEAD', 'GET', 'OPTIONS', 'PATCH', 'POST',
           'PUT', 'TRACE')
"""The standard HTTP methods.

.. note:: **TODO:**
    convert to an :class:`~spruce.lang._datatypes._misc.enum`

"""
