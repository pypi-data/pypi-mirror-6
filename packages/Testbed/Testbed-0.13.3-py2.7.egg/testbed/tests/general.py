#!/usr/bin/env python

""":mod:`General <testbed.resources._general>` tests."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import unittest as _unittest

import bedframe.webtypes as _webtypes
import napper as _napper
import spruce.logging as _logging

import testbed.testing as _testbedtest


class TestGeneral(_testbedtest.TestTestbed):

    def assert_noop_response(self, response):
        self.assert_return_response(response)
        null = _napper.extract_retval(response, self._noop_returntype)
        self.assertEqual(null, self._noop_expected_value)

    def test_get_noop(self):
        response = self.request('get', self._noop_path)
        self.assert_noop_response(response)

    def test_get_noop_with_trailing_pathsep(self):
        response = self.request('get', self._noop_path_with_trailing_pathsep)
        self.assert_noop_response(response)

    def test_post_noop(self):
        response = self.request('post', self._noop_path)
        self.assert_noop_response(response)

    def test_post_noop_with_trailing_pathsep(self):
        response = self.request('post', self._noop_path_with_trailing_pathsep)
        self.assert_noop_response(response)

    def test_postget_noop(self):
        response = self.request('postget', self._noop_path)
        self.assert_noop_response(response)

    def test_postget_noop_with_trailing_pathsep(self):
        response = self.request('postget',
                                self._noop_path_with_trailing_pathsep)
        self.assert_noop_response(response)

    @property
    def webservice_path(self):
        return '/general'

    @property
    def webservice_probe_path(self):
        return self._noop_path

    @property
    def _noop_expected_value(self):
        return None

    @property
    def _noop_path(self):
        return 'noop'

    @property
    def _noop_path_with_trailing_pathsep(self):
        return 'noop/'

    @property
    def _noop_returntype(self):
        return _webtypes.null


class _TestGeneralCorsPreflightMixin(object):
    def assert_noop_response(self, response):
        self.assert_cors_preflight_accepted_response(response)


class _TestGeneralCorsWithUntrustedOriginMixin(object):
    @property
    def expect_cors_origin_allowed(self):
        return True


class TestGeneralCorsActualWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin, _testbedtest.TestCorsActual,
           TestGeneral):
    pass


class TestGeneralCorsActualWithUntrustedOrigin\
          (_TestGeneralCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsActual, TestGeneral):
    pass


class TestGeneralCorsPreflightWithTrustedOrigin\
          (_TestGeneralCorsPreflightMixin,
           _testbedtest.TestCorsWithTrustedOrigin,
           _testbedtest.TestCorsPreflight, TestGeneral):
    pass


class TestGeneralCorsPreflightWithUntrustedOrigin\
          (_TestGeneralCorsPreflightMixin,
           _TestGeneralCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsPreflight, TestGeneral):
    pass


if __name__ == '__main__':
    _logging.basicConfig()
    _unittest.main()
