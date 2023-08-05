#!/usr/bin/env python

""":mod:`Authentication <testbed.resources._auth>` tests."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import unittest as _unittest

import spruce.logging as _logging
import testbed.testing as _testbedtest


class TestWelcomeBasic(_testbedtest.TestWelcome):
    @property
    def _welcome_path(self):
        return 'welcome_basic'


class TestWelcomeBasicWithLdapSimpleBackend\
          (_testbedtest.TestWelcomeWithLdapBackend):
    @property
    def _welcome_path(self):
        return 'welcome_basic_ldap_simple'


class TestWelcomeDigest(_testbedtest.TestWelcome):

    @_unittest.expectedFailure
    def test_get_with_no_creds_then_wrong_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_get_with_right_creds_then_wrong(self):
        self.fail()

    @_unittest.expectedFailure
    def test_get_with_wrong_creds(self):
        self.fail()

    @_unittest.expectedFailure
    def test_get_with_wrong_creds_then_none_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_get_with_wrong_creds_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_no_creds_then_wrong_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_right_creds_then_wrong(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_wrong_creds(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_wrong_creds_then_none_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_wrong_creds_then_right(self):
        self.fail()

    @property
    def _authtype(self):
        return 'digest'

    @property
    def _welcome_path(self):
        return 'welcome_digest'


class TestWelcomeDigestWithLdapGetPasswordBackend\
          (_testbedtest.TestWelcomeWithLdapBackend):

    @_unittest.expectedFailure
    def test_get_with_no_creds_then_wrong_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_get_with_right_creds_then_wrong(self):
        self.fail()

    @_unittest.expectedFailure
    def test_get_with_wrong_creds(self):
        self.fail()

    @_unittest.expectedFailure
    def test_get_with_wrong_creds_then_none_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_get_with_wrong_creds_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_no_creds_then_wrong_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_right_creds_then_wrong(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_wrong_creds(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_wrong_creds_then_none_then_right(self):
        self.fail()

    @_unittest.expectedFailure
    def test_postget_with_wrong_creds_then_right(self):
        self.fail()

    @property
    def _authtype(self):
        return 'digest'

    @property
    def _welcome_path(self):
        return 'welcome_digest_ldap_getpass'


class _TestWelcomeCorsWithUntrustedOriginMixin(object):

    def assert_expected_return_response(self, response):
        self.assert_cors_rejected_response(response,
                                           exc_name='CorsOriginForbidden')

    def assert_unauth_with_no_creds_response(self, response):
        self.assert_cors_rejected_response(response,
                                           exc_name='CorsOriginForbidden')

    def assert_unauth_with_wrong_creds_response(self, response):
        self.assert_cors_rejected_response(response,
                                           exc_name='CorsOriginForbidden')


class _TestWelcomeCorsPreflightWithTrustedOriginMixin(object):

    def assert_expected_return_response(self, response):
        self.assert_cors_preflight_accepted_response(response,
                                                     allowed_credentials=True)

    def assert_unauth_with_no_creds_response(self, response):
        self.assert_cors_preflight_accepted_response(response,
                                                     allowed_credentials=True)

    def assert_unauth_with_wrong_creds_response(self, response):
        self.assert_cors_preflight_accepted_response(response,
                                                     allowed_credentials=True)


class TestWelcomeBasicCorsActualWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin, _testbedtest.TestCorsActual,
           TestWelcomeBasic):
    pass


class TestWelcomeBasicCorsActualWithUntrustedOrigin\
          (_TestWelcomeCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsActual, TestWelcomeBasic):
    pass


class TestWelcomeBasicCorsPreflightWithTrustedOrigin\
          (_TestWelcomeCorsPreflightWithTrustedOriginMixin,
           _testbedtest.TestCorsWithTrustedOrigin,
           _testbedtest.TestCorsPreflight, TestWelcomeBasic):
    pass


class TestWelcomeBasicCorsPreflightWithUntrustedOrigin\
          (_TestWelcomeCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsPreflight, TestWelcomeBasic):
    pass


if __name__ == '__main__':
    _logging.basicConfig()
    _unittest.main()
