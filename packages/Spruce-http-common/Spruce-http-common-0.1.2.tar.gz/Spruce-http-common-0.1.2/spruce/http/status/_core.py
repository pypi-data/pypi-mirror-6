"""Core objects."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from collections import Mapping as _Mapping
import httplib as _http


# 1xx informational -----------------------------------------------------------

CONTINUE = 100

SWITCHING_PROTOCOLS = 101

PROCESSING = 102

INFORMATIONAL_STATUSES = (CONTINUE, SWITCHING_PROTOCOLS, PROCESSING)


# 2xx success -----------------------------------------------------------------

OK = 200

CREATED = 201

ACCEPTED = 202

NON_AUTHORITATIVE_INFORMATION = 203

NO_CONTENT = 204

RESET_CONTENT = 205

PARTIAL_CONTENT = 206

MULTI_STATUS = 207

ALREADY_REPORTED = 208

IM_USED = 226

SUCCESS_STATUSES = (OK, CREATED, ACCEPTED, NON_AUTHORITATIVE_INFORMATION,
                    NO_CONTENT, RESET_CONTENT, PARTIAL_CONTENT, MULTI_STATUS,
                    ALREADY_REPORTED, IM_USED)


# 3xx redirection -------------------------------------------------------------

MULTIPLE_CHOICES = 300

MOVED_PERMANENTLY = 301

FOUND = 302

SEE_OTHER = 303

NOT_MODIFIED = 304

USE_PROXY = 305

SWITCH_PROXY = 306

TEMPORARY_REDIRECT = 307

PERMANENT_REDIRECT = 308

REDIRECTION_STATUSES = (MULTIPLE_CHOICES, MOVED_PERMANENTLY, FOUND, SEE_OTHER,
                        NOT_MODIFIED, USE_PROXY, SWITCH_PROXY,
                        TEMPORARY_REDIRECT, PERMANENT_REDIRECT)


# 4xx client error ------------------------------------------------------------

BAD_REQUEST = 400

UNAUTHORIZED = 401

PAYMENT_REQUIRED = 402

FORBIDDEN = 403

NOT_FOUND = 404

METHOD_NOT_ALLOWED = 405

NOT_ACCEPTABLE = 406

PROXY_AUTHENTICATION_REQUIRED = 407

REQUEST_TIMEOUT = 408

CONFLICT = 409

GONE = 410

LENGTH_REQUIRED = 411

PRECONDITION_FAILED = 412

REQUEST_ENTITY_TOO_LARGE = 413

REQUEST_URI_TOO_LONG = 414

UNSUPPORTED_MEDIA_TYPE = 415

REQUESTED_RANGE_NOT_SATISFIABLE = 416

EXPECTATION_FAILED = 417

IM_A_TEAPOT = 418

ENHANCE_YOUR_CALM = 420

UNPROCESSABLE_ENTITY = 422

LOCKED = 423

FAILED_DEPENDENCY = 424

METHOD_FAILURE = 424

UNORDERED_COLLECTION = 425

UPGRADE_REQUIRED = 426

PRECONDITION_REQUIRED = 428

TOO_MANY_REQUESTS = 429

REQUEST_HEADER_FIELDS_TOO_LARGE = 431

NO_RESPONSE = 444

RETRY_WITH = 449

BLOCKED_BY_WINDOWS_PARENTAL_CONTROLS = 450

CLIENT_CLOSED_REQUEST = 499

CLIENT_ERROR_STATUSES = (BAD_REQUEST,
                         UNAUTHORIZED,
                         PAYMENT_REQUIRED,
                         FORBIDDEN,
                         NOT_FOUND,
                         METHOD_NOT_ALLOWED,
                         NOT_ACCEPTABLE,
                         PROXY_AUTHENTICATION_REQUIRED,
                         REQUEST_TIMEOUT,
                         CONFLICT,
                         GONE,
                         LENGTH_REQUIRED,
                         PRECONDITION_FAILED,
                         REQUEST_ENTITY_TOO_LARGE,
                         REQUEST_URI_TOO_LONG,
                         UNSUPPORTED_MEDIA_TYPE,
                         REQUESTED_RANGE_NOT_SATISFIABLE,
                         EXPECTATION_FAILED,
                         IM_A_TEAPOT,
                         ENHANCE_YOUR_CALM,
                         UNPROCESSABLE_ENTITY,
                         LOCKED,
                         FAILED_DEPENDENCY,
                         METHOD_FAILURE,
                         UNORDERED_COLLECTION,
                         UPGRADE_REQUIRED,
                         PRECONDITION_REQUIRED,
                         TOO_MANY_REQUESTS,
                         REQUEST_HEADER_FIELDS_TOO_LARGE,
                         NO_RESPONSE,
                         RETRY_WITH,
                         BLOCKED_BY_WINDOWS_PARENTAL_CONTROLS,
                         CLIENT_CLOSED_REQUEST,
                         )


# 5xx server error ------------------------------------------------------------

INTERNAL_SERVER_ERROR = 500

NOT_IMPLEMENTED = 501

BAD_GATEWAY = 502

SERVICE_UNAVAILABLE = 503

GATEWAY_TIMEOUT = 504

HTTP_VERSION_NOT_SUPPORTED = 505

VARIANT_ALSO_NEGOTIATES = 506

INSUFFICIENT_STORAGE = 507

LOOP_DETECTED = 508

BANDWIDTH_LIMIT_EXCEEDED = 509

NOT_EXTENDED = 510

NETWORK_AUTHENTICATION_REQUIRED = 511

NETWORK_READ_TIMEOUT_ERROR = 598

NETWORK_CONNECT_TIMEOUT_ERROR = 599

SERVER_ERROR_STATUSES = (INTERNAL_SERVER_ERROR,
                         NOT_IMPLEMENTED,
                         BAD_GATEWAY,
                         SERVICE_UNAVAILABLE,
                         GATEWAY_TIMEOUT,
                         HTTP_VERSION_NOT_SUPPORTED,
                         VARIANT_ALSO_NEGOTIATES,
                         INSUFFICIENT_STORAGE,
                         LOOP_DETECTED,
                         BANDWIDTH_LIMIT_EXCEEDED,
                         NOT_EXTENDED,
                         NETWORK_AUTHENTICATION_REQUIRED,
                         NETWORK_READ_TIMEOUT_ERROR,
                         NETWORK_CONNECT_TIMEOUT_ERROR,
                         )


class _StatusMessages(_Mapping):

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super(_StatusMessages, cls).__new__(cls)
        return cls._inst

    def __init__(self):
        self._keys = set(_http.responses.keys() + self._responses.keys())

    def __getitem__(self, code):
        try:
            return _http.responses[code]
        except KeyError:
            return self._responses[code]

    def __iter__(self):
        return iter(self._keys)

    def __len__(self):
        return len(self._keys)

    _inst = None

    _responses = {PROCESSING: 'Processing',
                  MULTI_STATUS: 'Multi-Status',
                  ALREADY_REPORTED: 'Already Reported',
                  IM_USED: 'IM Used',
                  PERMANENT_REDIRECT: 'Permanent Redirect',
                  IM_A_TEAPOT: 'I\'m a teapot',
                  ENHANCE_YOUR_CALM: 'Enhance Your Calm',
                  UNPROCESSABLE_ENTITY: 'Unprocessable Entity',
                  LOCKED: 'Locked',
                  FAILED_DEPENDENCY: 'Failed Dependency',
                  UNORDERED_COLLECTION: 'Unordered Collection',
                  UPGRADE_REQUIRED: 'Upgrade Required',
                  PRECONDITION_REQUIRED: 'Precondition Required',
                  TOO_MANY_REQUESTS: 'Too Many Requests',
                  REQUEST_HEADER_FIELDS_TOO_LARGE:
                      'Request Header Fields Too Large',
                  NO_RESPONSE: 'No Response',
                  RETRY_WITH: 'Retry With',
                  BLOCKED_BY_WINDOWS_PARENTAL_CONTROLS:
                      'Blocked by Windows Parental Controls',
                  CLIENT_CLOSED_REQUEST: 'Client Closed Request',
                  VARIANT_ALSO_NEGOTIATES: 'Variant Also Negotiates',
                  INSUFFICIENT_STORAGE: 'Insufficient Storage',
                  LOOP_DETECTED: 'Loop Detected',
                  BANDWIDTH_LIMIT_EXCEEDED: 'Bandwidth Limit Exceeded',
                  NOT_EXTENDED: 'Not Extended',
                  NETWORK_AUTHENTICATION_REQUIRED:
                      'Network Authentication Required',
                  NETWORK_READ_TIMEOUT_ERROR: 'Network read timeout error',
                  NETWORK_CONNECT_TIMEOUT_ERROR:
                      'Network connect timeout error',
                  }


status_messages = _StatusMessages()


def status_str(code):
    try:
        message = status_messages[code]
    except KeyError:
        return str(code)
    else:
        return '{} ({})'.format(message, code)


def statuscode_def_source(code):
    if code in (OK, CREATED, ACCEPTED, NO_CONTENT, MULTIPLE_CHOICES,
                MOVED_PERMANENTLY, FOUND, NOT_MODIFIED, BAD_REQUEST,
                UNAUTHORIZED, FORBIDDEN, NOT_FOUND, INTERNAL_SERVER_ERROR,
                NOT_IMPLEMENTED, BAD_GATEWAY, SERVICE_UNAVAILABLE):
        return 'HTTP/1.0 (RFC 1945)'
    elif code in (VARIANT_ALSO_NEGOTIATES,):
        return 'Transparent Content Negotiation in HTTP (RFC 2295)'
    elif code in (IM_A_TEAPOT,):
        return 'HTCPCP (RFC 2324)'
    elif code in (NOT_EXTENDED,):
        return 'An HTTP Extension Framework (RFC 2774)'
    elif code in (PROCESSING, MULTI_STATUS, UNPROCESSABLE_ENTITY, LOCKED,
                  FAILED_DEPENDENCY, INSUFFICIENT_STORAGE):
        return 'WebDAV (RFC 4918)'
    elif code in (CONTINUE, SWITCHING_PROTOCOLS, NON_AUTHORITATIVE_INFORMATION,
                  RESET_CONTENT, PARTIAL_CONTENT, SEE_OTHER, USE_PROXY,
                  SWITCH_PROXY, TEMPORARY_REDIRECT, PAYMENT_REQUIRED,
                  METHOD_NOT_ALLOWED, NOT_ACCEPTABLE,
                  PROXY_AUTHENTICATION_REQUIRED, REQUEST_TIMEOUT, CONFLICT,
                  GONE, LENGTH_REQUIRED, PRECONDITION_FAILED,
                  REQUEST_ENTITY_TOO_LARGE, REQUEST_URI_TOO_LONG,
                  UNSUPPORTED_MEDIA_TYPE, REQUESTED_RANGE_NOT_SATISFIABLE,
                  EXPECTATION_FAILED, GATEWAY_TIMEOUT,
                  HTTP_VERSION_NOT_SUPPORTED):
        return 'HTTP/1.1 (RFC 2616)'
    elif code in (UPGRADE_REQUIRED,):
        return 'Upgrading to TLS Within HTTP/1.1 (RFC 2817)'
    elif code in (IM_USED,):
        return 'Delta encoding in HTTP (RFC 3229)'
    elif code in (ALREADY_REPORTED, LOOP_DETECTED):
        return 'WebDAV BIND (RFC 5842)'
    elif code in (PRECONDITION_REQUIRED, TOO_MANY_REQUESTS,
                  REQUEST_HEADER_FIELDS_TOO_LARGE,
                  NETWORK_AUTHENTICATION_REQUIRED):
        return 'Additional HTTP Status Codes (RFC 6585)'
    elif code in (PERMANENT_REDIRECT, UNORDERED_COLLECTION):
        return 'Internet-Draft'
    elif code in (BANDWIDTH_LIMIT_EXCEEDED,):
        return 'Apache bw/limited extension'
    elif code in (RETRY_WITH, BLOCKED_BY_WINDOWS_PARENTAL_CONTROLS,
                  NETWORK_READ_TIMEOUT_ERROR, NETWORK_CONNECT_TIMEOUT_ERROR):
        return 'Microsoft'
    elif code in (NO_RESPONSE, CLIENT_CLOSED_REQUEST):
        return 'nginx'
    elif code in (ENHANCE_YOUR_CALM,):
        return 'Twitter'


statuscodes = status_messages.keys()
