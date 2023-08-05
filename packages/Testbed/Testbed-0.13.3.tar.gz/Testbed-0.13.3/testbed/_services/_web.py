"""Web services."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import re as _re

import bedframe as _bedframe
import bedframe.auth as _bedframe_auth
import bedframe.auth.digest as _bedframe_digest_auth
import bedframe.auth.http as _bedframe_http_auth
import bedframe.auth.plain as _bedframe_plain_auth

from .. import _cors as _testbed_cors
from .. import resources as _testbed_resources


class TestbedService(_bedframe.WebService):
    def __init__(self, impl, resources=None, auth_spaces=None,
                 cors_affordancesets=None, **kwargs):

        welcome_basic_provisions = _bedframe_auth.SECPROV_CLIENT_AUTH
        #welcome_digest_provisions = \
        #    _bedframe_auth.SECPROV_CLIENT_AUTH \
        #        | _bedframe_auth.SECPROV_CLIENT_ENCRYPTED_SECRET \
        #        | _bedframe_auth.SECPROV_SERVER_NONCE
        #welcome_digest_maxsec_provisions = \
        #    _bedframe_auth.SECPROV_CLIENT_AUTH \
        #        | _bedframe_auth.SECPROV_CLIENT_ENCRYPTED_SECRET \
        #        | _bedframe_auth.SECPROV_SERVER_NONCE \
        #        | _bedframe_auth.SECPROV_SERVER_NONCE_PER_REQUEST \
        #        | _bedframe_auth.SECPROV_SERVER_NONCE_USE_COUNT \
        #        | _bedframe_auth.SECPROV_CLIENT_NONCE \
        #        | _bedframe_auth.SECPROV_REQUEST_ENTITY_INTEGRITY

        # resources -----------------------------------------------------------

        resources = _bedframe.WebResourceMap(resources)
        resources_ = \
            {r'(?:/cors)?/auth/welcome_basic':
                 _testbed_resources.Welcome
                  .partial_inst(auth_provisions=welcome_basic_provisions),
             r'(?:/cors)?/auth/welcome_basic_ldap_simple':
                 _testbed_resources.Welcome
                  .partial_inst(auth_provisions=welcome_basic_provisions),
             r'(?:/cors)?/auth/welcome_digest':
                 _testbed_resources.Welcome
                  .partial_inst(auth_provisions=welcome_basic_provisions),
             r'(?:/cors)?/auth/welcome_digest_ldap_getpass':
                 _testbed_resources.Welcome
                  .partial_inst(auth_provisions=welcome_basic_provisions),
             #r'(?:/cors)?/auth/welcome_digest_maxsec':
             #    _testbed_resources.Welcome
             #     .partial_inst(auth_provisions=
             #                       welcome_digest_maxsec_provisions),
             r'(?:/cors)?/datetime/difference':
                 _testbed_resources.DatetimeDifference,
             r'(?:/cors)?/datetime/echo': _testbed_resources.DatetimeEcho,
             r'(?:/cors)?/datetime/now': _testbed_resources.DatetimeNow,
             r'(?:/cors)?/datetime/sum': _testbed_resources.DatetimeSum,
             r'(?:/cors)?/echo/echo_methodargs':
                 _testbed_resources.EchoMethodArgs,
             r'(?:/cors)?/echo/echo_pathargs(?:/(?:{}))*'
              .format('|'.join(r'(?:{arg}_(?P<{arg}>[^{seps}]*))'
                                .format(arg=arg,
                                        seps=_re.escape(resources.seps))
                               for arg
                               in _testbed_resources.EchoResourceArgs
                                      .__init__.argnames)):
                 _testbed_resources.EchoResourceArgs,
             r'(?:/cors)?/echo/echo_pathpartargs':
                 _testbed_resources.EchoResourceArgs,
             r'(?:/cors)?/echo/echo_string_methodarg':
                 _testbed_resources.EchoStringMethodArg,
             r'(?:/cors)?/echo/echo_string_patharg/(?P<string>[^{seps}]*)'
              .format(seps=_re.escape(resources.seps)):
                 _testbed_resources.EchoStringResourceArg,
             r'(?:/cors)?/echo/echo_string_pathpartarg':
                 _testbed_resources.EchoStringResourceArg,
             r'(?:/cors)?/echo/echo_variadic_methodargs':
                 _testbed_resources.EchoVariadicMethodArgs,
             r'(?:/cors)?/echo/echo_variadic_pathargs(?:/(?:{}))*'
              .format('|'.join(r'(?:{arg}_(?P<{arg}>[^{seps}]*))'
                                .format(arg=arg,
                                        seps=_re.escape(resources.seps))
                               for arg
                               in _testbed_resources.EchoVariadicResourceArgs
                                      .__init__.argnames)):
                 _testbed_resources.EchoVariadicResourceArgs,
             r'(?:/cors)?/echo/echo_variadic_pathpartargs':
                 _testbed_resources.EchoVariadicResourceArgs,
             r'(?:/cors)?/exc/runtime_error': _testbed_resources.RuntimeError,
             r'(?:/cors)?/general/noop': _testbed_resources.NoOp,
             r'(?:/cors)?/redirect/response':
                 _testbed_resources.ResponseRedirection,
             r'/performance/noop': _testbed_resources.NoOp,
             r'/performance/sleep': _testbed_resources.Sleep,
             }
        resources_.update(resources or {})

        # CORS settings -------------------------------------------------------

        cors_affordancesets_ = \
            {r'/cors': _bedframe.CorsAffordanceSet
                        (origins=(_testbed_cors.TRUSTED_ORIGIN,),
                         methods='*', request_headers='*',
                         exposed_response_headers='*'),
             r'/cors/general/noop': _bedframe.CorsAffordanceSet.max(),
             }
        cors_affordancesets_.update(cors_affordancesets or {})

        super(TestbedService, self)\
         .__init__(impl, resources=resources_,
                   cors_affordancesets=cors_affordancesets_, **kwargs)

        # auth algorithms -----------------------------------------------------

        plain_auth = \
            _bedframe_plain_auth.PlainAuth(authenticator=self.authenticator)
        self.auth_algorithms.append(plain_auth)
        digest_auth = \
            _bedframe_digest_auth.DigestAuth(authenticator=self.authenticator)
        self.auth_algorithms.append(digest_auth)

        # auth connectors -----------------------------------------------------

        non_session_login_clerks = \
            [clerk for clerk in self.auth_clerks
             if not isinstance(clerk,
                               _bedframe_http_auth.HttpSessionLoginClerk)]

        # auth spaces ---------------------------------------------------------

        auth_spaces_ = \
            {r'(?:/cors)?/auth/welcome_basic':
                 _bedframe_auth.Space
                  (realms=('inmemory.testbed',),
                   provisionsets=(welcome_basic_provisions,),
                   algorithms=(plain_auth,),
                   clerks=non_session_login_clerks),
             r'(?:/cors)?/auth/welcome_basic_ldap_simple':
                 _bedframe_auth.Space
                  (realms=('ldap.testbed',),
                   provisionsets=(welcome_basic_provisions,),
                   algorithms=(plain_auth,),
                   clerks=non_session_login_clerks),
             r'(?:/cors)?/auth/welcome_digest':
                 _bedframe_auth.Space
                  (realms=('inmemory.testbed',),
                   provisionsets=(welcome_basic_provisions,),
                   algorithms=(digest_auth,),
                   clerks=non_session_login_clerks),
             r'(?:/cors)?/auth/welcome_digest_ldap_getpass':
                 _bedframe_auth.Space
                  (realms=('ldap.testbed',),
                   provisionsets=(welcome_basic_provisions,),
                   algorithms=(digest_auth,),
                   clerks=non_session_login_clerks),
             }
        auth_spaces_.update(auth_spaces or {})
        self.auth_spaces.update(auth_spaces_)
