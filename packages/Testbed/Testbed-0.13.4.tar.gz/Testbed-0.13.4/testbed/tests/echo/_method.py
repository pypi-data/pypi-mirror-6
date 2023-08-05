#!/usr/bin/env python

""":mod:`Echo <testbed.resources._echo>` tests."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import unittest as _unittest

import spruce.logging as _logging

import testbed.testing as _testbedtest
from . import _core as _echo_tests_core


# echo args tests -------------------------------------------------------------


class TestEchoMethodArgs(_echo_tests_core.TestEchoArgs):

    @property
    def webservice_probe_path(self):
        return self._echo_variadic_methodargs_path

    @property
    def _echo_methodargs_path(self):
        return 'echo_methodargs'

    @property
    def _echo_variadic_methodargs_path(self):
        return 'echo_variadic_methodargs'


class TestEchoBodyArgs(TestEchoMethodArgs):

    def test_post_echo_bodyargs(self):
        response = self.request('post',
                                self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='body')
        self.assert_echo_args_response(response)

    def test_post_echo_bodyargs_as_html(self):
        response = self.request('post',
                                self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='body',
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')

    def test_post_echo_variadic_bodyargs(self):
        response = self.request('post',
                                self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='body')
        self.assert_echo_args_response(response)

    def test_post_echo_variadic_bodyargs_as_html(self):
        response = self.request('post',
                                self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='body',
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')

    def test_postget_echo_bodyargs(self):
        response = self.request('postget',
                                self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='body')
        self.assert_echo_args_response(response)

    def test_postget_echo_bodyargs_as_html(self):
        response = self.request('postget',
                                self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='body',
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')

    def test_postget_echo_variadic_bodyargs(self):
        response = self.request('postget',
                                self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='body')
        self.assert_echo_args_response(response)

    def test_postget_echo_variadic_bodyargs_as_html(self):
        response = self.request('postget',
                                self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='body',
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')


class TestEchoQueryArgs(TestEchoMethodArgs):

    def test_get_echo_queryargs(self):
        response = self.request('get', self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes)
        self.assert_echo_args_response(response)

    def test_get_echo_queryargs_as_html(self):
        response = self.request('get', self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')

    def test_get_echo_variadic_queryargs(self):
        response = self.request('get', self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes)
        self.assert_echo_args_response(response)

    def test_get_echo_variadic_queryargs_as_html(self):
        response = self.request('get', self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')

    def test_post_echo_queryargs(self):
        response = self.request('post',
                                self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='query')
        self.assert_echo_args_response(response)

    def test_post_echo_queryargs_as_html(self):
        response = self.request('post',
                                self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='query',
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')

    def test_post_echo_variadic_queryargs(self):
        response = self.request('post',
                                self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='query')
        self.assert_echo_args_response(response)

    def test_post_echo_variadic_queryargs_as_html(self):
        response = self.request('post',
                                self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='query',
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')

    def test_postget_echo_queryargs(self):
        response = self.request('postget',
                                self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='query')
        self.assert_echo_args_response(response)

    def test_postget_echo_queryargs_as_html(self):
        response = self.request('postget',
                                self._echo_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='query',
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')

    def test_postget_echo_variadic_queryargs(self):
        response = self.request('postget',
                                self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='query')
        self.assert_echo_args_response(response)

    def test_postget_echo_variadic_queryargs_as_html(self):
        response = self.request('postget',
                                self._echo_variadic_methodargs_path,
                                self._echo_args_args,
                                argtypes=self._echo_args_argtypes,
                                args_as='query',
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_echo_args_response(response, contenttype='text/html')


# echo string arg tests -------------------------------------------------------


class _TestEchoStringMethodArg(_echo_tests_core.TestEchoStringArg):
    @property
    def _path(self):
        return 'echo_string_methodarg'


class TestEchoStringBodyArg(_TestEchoStringMethodArg):

    def test_post_arg_allvalues(self):
        self._test_request_arg_allvalues('post')

    def test_post_arg_allvalues_as_html(self):
        self._test_request_arg_allvalues('post',
                                         accept_mediaranges=('text/html',
                                                             '*/*; q=0.01'),
                                         contenttype='text/html')

    def test_postget_arg_allvalues(self):
        self._test_request_arg_allvalues('postget')

    def test_postget_arg_allvalues_as_html(self):
        self._test_request_arg_allvalues('postget',
                                         accept_mediaranges=('text/html',
                                                             '*/*; q=0.01'),
                                         contenttype='text/html')

    def _request_arg(self, method, string, **kwargs):
        return self.request(method, self._path, {'string': string},
                            argtypes=self._argtypes, args_as='body', **kwargs)


class TestEchoUrlEncodedStringBodyArg(TestEchoStringBodyArg):
    def _request_arg(self, method, string, **kwargs):
        return self.request(method, self._path, {'string': string},
                            argtypes=self._argtypes, args_as='body_urlencoded',
                            **kwargs)


class TestEchoStringQueryArg(_TestEchoStringMethodArg):

    def test_get_arg_allvalues(self):
        self._test_request_arg_allvalues('get')

    def test_get_arg_allvalues_as_html(self):
        self._test_request_arg_allvalues('get',
                                         accept_mediaranges=('text/html',
                                                             '*/*; q=0.01'),
                                         contenttype='text/html')

    def test_post_arg_allvalues(self):
        self._test_request_arg_allvalues('post')

    def test_post_arg_allvalues_as_html(self):
        self._test_request_arg_allvalues('post',
                                         accept_mediaranges=('text/html',
                                                             '*/*; q=0.01'),
                                         contenttype='text/html')

    def test_postget_arg_allvalues(self):
        self._test_request_arg_allvalues('postget')

    def test_postget_arg_allvalues_as_html(self):
        self._test_request_arg_allvalues('postget',
                                         accept_mediaranges=('text/html',
                                                             '*/*; q=0.01'),
                                         contenttype='text/html')

    def _request_arg(self, method, string, **kwargs):
        return self.request(method, self._path, {'string': string},
                            argtypes=self._argtypes, args_as='query', **kwargs)


# CORS tests ------------------------------------------------------------------


class TestEchoBodyArgsCorsActualWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin, _testbedtest.TestCorsActual,
           TestEchoBodyArgs):
    pass


class TestEchoBodyArgsCorsActualWithUntrustedOrigin\
          (_echo_tests_core.TestEchoArgsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsActual, TestEchoBodyArgs):
    pass


class TestEchoBodyArgsCorsPreflightWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin,
           _testbedtest.TestCorsPreflight, TestEchoBodyArgs):
    def assert_echo_args_response(self, response, **kwargs):
        self.assert_cors_preflight_accepted_response(response, **kwargs)


class TestEchoBodyArgsCorsPreflightWithUntrustedOrigin\
          (_echo_tests_core.TestEchoArgsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsPreflight, TestEchoBodyArgs):
    pass


class TestEchoQueryArgsCorsActualWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin, _testbedtest.TestCorsActual,
           TestEchoQueryArgs):
    pass


class TestEchoQueryArgsCorsActualWithUntrustedOrigin\
          (_echo_tests_core.TestEchoArgsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsActual, TestEchoQueryArgs):
    pass


class TestEchoQueryArgsCorsPreflightWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin,
           _testbedtest.TestCorsPreflight, TestEchoQueryArgs):
    def assert_echo_args_response(self, response, **kwargs):
        self.assert_cors_preflight_accepted_response(response, **kwargs)


class TestEchoQueryArgsCorsPreflightWithUntrustedOrigin\
          (_echo_tests_core.TestEchoArgsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsPreflight, TestEchoQueryArgs):
    pass


if __name__ == '__main__':
    _logging.basicConfig()
    _unittest.main()
