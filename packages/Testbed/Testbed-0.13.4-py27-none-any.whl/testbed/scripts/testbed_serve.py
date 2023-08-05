#!/usr/bin/env python

"""Launch the testbed web service."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import argparse as _argparse
import re as _re
import sys as _sys
import traceback as _traceback

import bedframe as _bedframe
import bedframe.auth.ldap as _bedframe_ldap_auth
import bedframe.testing as _bedtest
from spruce.collections import odict as _odict
import spruce.ldap.testing as _ldaptest
import spruce.logging as _logging

import testbed as _testbed


def main():

    loglevel = _logging.WARNING
    _logger.setLevel(level=loglevel)
    _log_formatter = _logging.Formatter(_LOGGING_FORMAT)
    _log_handler = _logging.StreamHandler()
    _log_handler.setFormatter(_log_formatter)
    _logger.addHandler(_log_handler)

    try:
        args = _parse_args()

        loglevel = _LOGLEVELS_BY_ARGVALUE[args.loglevel]
        _logger.setLevel(loglevel)

        _run(args)
    except _CriticalErrorWrapper as exc:
        _logger.critical(_format_exc(exc))
        _sys.exit(1)
    except RuntimeError as exc:
        _logger.error(_format_exc(exc))
        _sys.exit(1)


def _format_exc(exc, limit=None):
    message = str(exc)
    if _logger.isEnabledFor(_logging.DEBUG):
        message += '\n' + _traceback.format_exc(limit=limit)
    return message


def _parse_args():

    description = 'Launch the testbed web service.'

    debug_default = [_debug_flag_argname(flag)
                     for flag in _bedframe.DebugFlagSet.valid_flags()
                     if flag in _bedframe.DEBUG_DEFAULT]

    parser = \
        _argparse.ArgumentParser(description=description,
                                 formatter_class=
                                     _argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--port', type=int, default=80,
                        help='listen for requests on the specified port')
    parser.add_argument('--debug', nargs='*',
                        choices=_DEBUG_FLAGS_BY_ARGVALUE.keys(),
                        default=debug_default, help='debugging flags')
    parser.add_argument('--loglevel',
                        choices=
                            sorted(_LOGLEVELS_BY_ARGVALUE.keys(),
                                   key=(lambda value:
                                            -_LOGLEVELS_BY_ARGVALUE[value])),
                        default='warning',
                        help='the logging level')
    return parser.parse_args()


def _run(args):

    if args.debug == []:
        debug_flags = _bedframe.DEBUG_FULL
    else:
        debug_flags = _bedframe.DebugFlagSet()
        for value in args.debug:
            debug_flags |= _DEBUG_FLAGS_BY_ARGVALUE[value]

    # TODO: expose a means to connect to an existing LDAP service
    ldapservice = _ldaptest.LdapTestService()
    pid = ldapservice.start(fork=True)
    if pid == 0:
        _sys.exit()

    try:
        webservice = _testbed.TestbedService('tornado',
                                             uris=('http://localhost:{}'
                                                    .format(args.port),),
                                             debug_flags=debug_flags)

        inmemory_auth_realm = 'inmemory.testbed'
        ldap_auth_realm = 'ldap.testbed'
        auth_supplicants = \
            (_bedtest.InMemoryPlainSupplicant
              (_ldaptest.USERS, realm=inmemory_auth_realm,
               authenticator=webservice.authenticator),
             _bedtest.InMemoryGetPasswordSupplicant
              (_ldaptest.USERS, realm=inmemory_auth_realm,
               authenticator=webservice.authenticator),
             _bedframe_ldap_auth.LdapSimpleSupplicant
              (ldapservice.uris[0], realm=ldap_auth_realm,
               basedn=ldapservice.users_dn,
               authenticator=webservice.authenticator),
             _bedframe_ldap_auth.LdapGetPasswordSupplicant
              (ldapservice.uris[0],
               realm=ldap_auth_realm,
               basedn=ldapservice.users_dn,
               bind_dn=ldapservice.root_dn,
               bind_password=ldapservice.root_password,
               authenticator=webservice.authenticator),
             )
        webservice.auth_supplicants.extend(auth_supplicants)

        webservice.start()
    finally:
        # TODO: expose a means to connect to an existing LDAP service.  don't
        #     make this call in that case
        ldapservice.stop()


class _CriticalErrorWrapper(RuntimeError):

    """
    A wrapper for an exception after which it is unsafe or not useful to
    continue running the application.

    This object enables information hiding for an exception while preserving
    the original exception's traceback and message.

    When raised in an :keyword:`except` block, a :class:`_CriticalErrorWrapper`
    implicitly wraps the exception that was just caught, effectively
    re-raising it while marking it as a critical error.  This is useful for
    more generic layers of exception handling farther up the stack, which
    can then handle the exception as a critical error without concerning
    themselves about every possible type of critical error that might occur.

    The original exception object and traceback are retrieved automatically
    via :func:`sys.exc_info` and can be respectively accessed via
    :attr:`orig_exc` and :attr:`orig_tb`.

    .. note:: **TODO:** generalize and migrate

    """

    def __init__(self):
        _, self._orig_exc, self._orig_tb = _sys.exc_info()
        if self._orig_exc:
            super(_CriticalErrorWrapper, self).__init__(str(self._orig_exc))
        else:
            super(_CriticalErrorWrapper, self).__init__()

    @property
    def orig_exc(self):
        """The original exception that triggered this error.

        :type: :exc:`Exception`

        """
        return self._orig_exc

    @property
    def orig_tb(self):
        """
        The traceback of the original exception that triggered this error.

        :type: :class:`traceback`

        """
        return self._orig_tb


def _debug_flag_argname(flag):
    return _re.sub('^debug_', '',
                   _bedframe.DebugFlagSet.flag_name(flag).lower())

_DEBUG_FLAGS_BY_ARGVALUE = \
    _odict([('secure', _bedframe.DEBUG_SECURE),
            ('default', _bedframe.DEBUG_DEFAULT),
            ('full', _bedframe.DEBUG_FULL),
            ('exc_secure', _bedframe.DEBUG_EXC_SECURE),
            ('exc_default', _bedframe.DEBUG_EXC_DEFAULT),
            ('exc_full', _bedframe.DEBUG_EXC_FULL),
            ])
_DEBUG_FLAGS_BY_ARGVALUE.update([(_debug_flag_argname(flag), flag)
                                 for flag
                                 in _bedframe.DebugFlagSet.valid_flags()])


_logger = _logging.getLogger()

_LOGGING_FORMAT = '%(levelname)s: %(message)s'

_LOGLEVELS_BY_ARGVALUE = _odict([('critical', _logging.CRITICAL),
                                 ('error', _logging.ERROR),
                                 ('warning', _logging.WARNING),
                                 ('info', _logging.INFO),
                                 ('debug', _logging.DEBUG),
                                 ('insecure', _logging.INSECURE),
                                 ])


if __name__ == '__main__':
    main()
