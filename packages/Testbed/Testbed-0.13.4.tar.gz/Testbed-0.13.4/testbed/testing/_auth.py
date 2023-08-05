""":mod:`Authentication <testbed.resources._auth>` testing."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import abc as _abc

import bedframe.testing as _bedtest
import bedframe.webtypes as _webtypes
import napper as _napper
import spruce.ldap.testing as _ldaptest

from . import _core as _testbedtest_core


class TestWelcome(_testbedtest_core.TestTestbed):

    __metaclass__ = _abc.ABCMeta

    def assert_expected_return_response(self, response):
        self.assert_return_response(response)
        welcome = _napper.extract_retval(response, self._returntype)
        self.assertEqual(welcome, self._expected_value)

    def test_get_with_no_creds(self):
        self._test_get_with_no_creds()

    def test_get_with_no_creds_then_right(self):
        self._test_get_with_no_creds()
        self._test_get_with_right_creds()

    def test_get_with_no_creds_then_wrong_then_right(self):
        self._test_get_with_no_creds()
        self._test_get_with_wrong_creds()
        self._test_get_with_right_creds()

    def test_get_with_right_creds(self):
        self._test_get_with_right_creds()

    def test_get_with_right_creds_then_none(self):
        self._test_get_with_right_creds()
        self._test_get_with_no_creds()

    def test_get_with_right_creds_then_wrong(self):
        self._test_get_with_right_creds()
        self._test_get_with_wrong_creds()

    def test_get_with_wrong_creds(self):
        self._test_get_with_wrong_creds()

    def test_get_with_wrong_creds_then_none_then_right(self):
        self._test_get_with_wrong_creds()
        self._test_get_with_no_creds()
        self._test_get_with_right_creds()

    def test_get_with_wrong_creds_then_right(self):
        self._test_get_with_wrong_creds()
        self._test_get_with_right_creds()

    def test_postget_with_no_creds(self):
        self._test_postget_with_no_creds()

    def test_postget_with_no_creds_then_wrong_then_right(self):
        self._test_postget_with_no_creds()
        self._test_postget_with_wrong_creds()
        self._test_postget_with_right_creds()

    def test_postget_with_right_creds(self):
        self._test_postget_with_right_creds()

    def test_postget_with_right_creds_then_none(self):
        self._test_postget_with_right_creds()
        self._test_postget_with_no_creds()

    def test_postget_with_right_creds_then_wrong(self):
        self._test_postget_with_right_creds()
        self._test_postget_with_wrong_creds()

    def test_postget_with_wrong_creds(self):
        self._test_postget_with_wrong_creds()

    def test_postget_with_wrong_creds_then_none_then_right(self):
        self._test_postget_with_wrong_creds()
        self._test_postget_with_no_creds()
        self._test_postget_with_right_creds()

    def test_postget_with_wrong_creds_then_right(self):
        self._test_postget_with_wrong_creds()
        self._test_postget_with_right_creds()

    @property
    def webservice_path(self):
        return '/auth'

    @property
    def webservice_probe_path(self):
        return self._welcome_path

    @property
    def _authtype(self):
        return 'basic'

    @property
    def _expected_value(self):
        return 'Welcome, {}'.format(self._user)

    @property
    def _returntype(self):
        return _webtypes.unicode

    def _test_get_with_no_creds(self):
        response = self.request('get', self._welcome_path)
        self.assert_unauth_with_no_creds_response(response)

    def _test_get_with_right_creds(self):
        response = self.request('get', self._welcome_path,
                                auth=(self._user, self._user.password),
                                authtype=self._authtype)
        self.assert_expected_return_response(response)

    def _test_get_with_wrong_creds(self):
        response = self.request('get', self._welcome_path,
                                auth=(self._user, self._wrong_password),
                                authtype=self._authtype)
        self.assert_unauth_with_wrong_creds_response(response)

    def _test_postget_with_no_creds(self):
        response = self.request('postget', self._welcome_path)
        self.assert_unauth_with_no_creds_response(response)

    def _test_postget_with_right_creds(self):
        response = self.request('postget', self._welcome_path,
                                auth=(self._user, self._user.password),
                                authtype=self._authtype)
        self.assert_expected_return_response(response)

    def _test_postget_with_wrong_creds(self):
        response = self.request('postget', self._welcome_path,
                                auth=(self._user, self._wrong_password),
                                authtype=self._authtype)
        self.assert_unauth_with_wrong_creds_response(response)

    @property
    def _user(self):
        return _ldaptest.USERS[0]

    @_abc.abstractproperty
    def _welcome_path(self):
        pass

    @property
    def _wrong_password(self):
        return self._user.password + '1'


class TestWelcomeWithLdapBackend(_ldaptest.LdapTestServiceTestCase,
                                 _bedtest.WebServiceWithLdapTestCase,
                                 TestWelcome):
    pass
