#!/usr/bin/env python
# coding=utf-8

"""
defines exception types and constants
"""

import logging
logging.basicConfig(format='%(levelname)-8s %(message)s',
                    level=logging.INFO)
logger = logging.getLogger('cloudns')

logging.getLogger('requests').setLevel(logging.WARNING)

# some defined zone and record status.

PENDING_ACTIVE = 0

ACTIVE = 1

PENDING_REMOVAL = 2


class CloudnsError(Exception):
    pass


class CloudnsRuntimeError(CloudnsError, RuntimeError):
    pass


class CloudnsValidationError(CloudnsError):
    pass


class CloudnsBadUsage(CloudnsError):
    pass


class CloudnsServerError(CloudnsRuntimeError):
    """an error occurred on cloudns server, not your fault.

    """
    pass


class CloudnsAuthenticationFailure(CloudnsRuntimeError):
    pass


class RecordNotFound(CloudnsRuntimeError):
    pass


class DuplicateRecord(CloudnsRuntimeError):
    """raised when you want to create a duplicate record.

    two records are dup if zone, name, content, isp are all the same.

    """
    pass


class RecordNotReady(CloudnsRuntimeError):
    """raised when you delete a record that is in PENDING_ACTIVE status.

    """
    pass


class ErrorNumbers(object):
    """Error Numbers as defined in upstream api.

    """
    NOERROR = 0
    API_IS_NOT_SUPPORTED = 1
    HTTP_METHOD_IS_NOT_SUPPORTED = 2
    AUTHENTICATE_FAILED = 3
    PARA_IS_REQUIRED = 4    # missing required parameter
    PARA_IS_INVALID = 5     # parameter syntax error
    PERMISSION_DENIED = 6
    DUPLICATE_USER = 7
    DUPLICATE_ZONE = 8
    PROCESS_FAILED = 9
    UNEXPECT_RESULT = 10
    USER_IS_INVALID = 11
    ZONE_IS_INVALID = 12
    REMOTE_VALIDATE_FAILED = 13   # parameter semantics error
    UNCLASSIFY = 1000
