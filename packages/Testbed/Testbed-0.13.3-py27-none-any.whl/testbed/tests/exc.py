#!/usr/bin/env python

""":mod:`Exception-triggering <testbed.resources._exc>` tests."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import unittest as _unittest

import spruce.http.status as _http_status
import spruce.logging as _logging

import testbed.testing as _testbedtest


class TestExceptions(_testbedtest.TestTestbed):

    @property
    def webservice_path(self):
        return '/exc'

    @property
    def webservice_probe_path(self):
        return self._exc_path


class TestRuntimeError(TestExceptions):

    def assert_runtime_error_response(self, response, **kwargs):
        self.assert_exc_response(response,
                                 status=_http_status.INTERNAL_SERVER_ERROR,
                                 class_def_module='exceptions',
                                 name='RuntimeError',
                                 message_pattern='exceptionally expected',
                                 **kwargs)

    def test_get_runtime_error(self):
        response = self.request('get', self._exc_path)
        self.assert_runtime_error_response(response)

    def test_get_runtime_error_as_html(self):
        response = self.request('get', self._exc_path,
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_runtime_error_response(response, contenttype='text/html')

    def test_post_runtime_error(self):
        response = self.request('post', self._exc_path)
        self.assert_runtime_error_response(response)

    def test_post_runtime_error_as_html(self):
        response = self.request('post', self._exc_path,
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_runtime_error_response(response, contenttype='text/html')

    def test_postget_runtime_error(self):
        response = self.request('postget', self._exc_path)
        self.assert_runtime_error_response(response)

    def test_postget_runtime_error_as_html(self):
        response = self.request('postget', self._exc_path,
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_runtime_error_response(response, contenttype='text/html')

    @property
    def _exc_path(self):
        return 'runtime_error'


class _TestExceptionsCorsWithUntrustedOriginMixin(object):
    def assert_exc_response(self, response, **kwargs):
        kwargs_ = {}
        try:
            kwargs_['contenttype'] = kwargs['contenttype']
        except KeyError:
            pass
        self.assert_cors_rejected_response(response,
                                           exc_name='CorsOriginForbidden',
                                           **kwargs_)


class TestExceptionsCorsActualWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin, _testbedtest.TestCorsActual,
           TestExceptions):
    pass


class TestExceptionsCorsActualWithUntrustedOrigin\
          (_TestExceptionsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsActual, TestExceptions):
    pass


class TestExceptionsCorsPreflightWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin,
           _testbedtest.TestCorsPreflight, TestExceptions):
    def assert_exc_response(self, response, **kwargs):
        kwargs_ = {}
        try:
            kwargs_['contenttype'] = kwargs['contenttype']
        except KeyError:
            pass
        self.assert_cors_preflight_accepted_response(response, **kwargs_)


class TestExceptionsCorsPreflightWithUntrustedOrigin\
          (_TestExceptionsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsPreflight, TestExceptions):
    pass


if __name__ == '__main__':
    _logging.basicConfig()
    _unittest.main()
