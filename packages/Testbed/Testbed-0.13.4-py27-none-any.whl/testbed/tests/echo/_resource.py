#!/usr/bin/env python

""":mod:`Echo <testbed.resources._echo>` tests."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import abc as _abc
import json as _json
import unittest as _unittest
from urllib import quote as _percent_encode

import spruce.logging as _logging

import testbed.testing as _testbedtest
from . import _core as _echo_tests_core


# echo args tests -------------------------------------------------------------


class TestEchoPathArgs(_echo_tests_core.TestEchoArgs):

    def test_get_echo_pathargs(self):
        response = self.request('get', self._echo_pathargs_path)
        self.assert_echo_args_response(response)

    def test_get_echo_variadic_pathargs(self):
        response = self.request('get', self._echo_variadic_pathargs_path)
        self.assert_echo_args_response(response)

    def test_post_echo_pathargs(self):
        response = self.request('post', self._echo_pathargs_path)
        self.assert_echo_args_response(response)

    def test_post_echo_variadic_pathargs(self):
        response = self.request('post', self._echo_variadic_pathargs_path)
        self.assert_echo_args_response(response)

    def test_postget_echo_pathargs(self):
        response = self.request('postget', self._echo_pathargs_path)
        self.assert_echo_args_response(response)

    def test_postget_echo_variadic_pathargs(self):
        response = self.request('postget', self._echo_variadic_pathargs_path)
        self.assert_echo_args_response(response)

    @property
    def webservice_probe_path(self):
        return self._echo_variadic_pathargs_path

    @property
    def _echo_pathargs_path(self):
        return '/'.join(['echo_pathargs']
                        + ['{}_{}'.format(name,
                                          _percent_encode(_json.dumps(value)))
                           for name, value in self._echo_args_args.items()])

    @property
    def _echo_variadic_pathargs_path(self):
        return '/'.join(['echo_variadic_pathargs']
                        + ['{}_{}'.format(name,
                                          _percent_encode(_json.dumps(value)))
                           for name, value
                           in self._echo_args_args.items()])


class TestEchoPathPartArgs(_echo_tests_core.TestEchoArgs):

    def test_get_echo_ordered_pathpartargs(self):
        response = self.request('get', self._echo_ordered_pathpartargs_path)
        self.assert_echo_args_response(response)

    def test_get_echo_variadic_ordered_pathpartargs(self):
        response = self.request('get',
                                self._echo_variadic_ordered_pathpartargs_path)
        self.assert_echo_args_response(response)

    def test_post_echo_ordered_pathpartargs(self):
        response = self.request('post', self._echo_ordered_pathpartargs_path)
        self.assert_echo_args_response(response)

    def test_post_echo_variadic_ordered_pathpartargs(self):
        response = self.request('get',
                                self._echo_variadic_ordered_pathpartargs_path)
        self.assert_echo_args_response(response)

    def test_postget_echo_ordered_pathpartargs(self):
        response = self.request('postget',
                                self._echo_ordered_pathpartargs_path)
        self.assert_echo_args_response(response)

    def test_postget_echo_variadic_ordered_pathpartargs(self):
        response = self.request('postget',
                                self._echo_variadic_ordered_pathpartargs_path)
        self.assert_echo_args_response(response)

    @property
    def _echo_ordered_pathpartargs_path(self):
        return '&'.join(['echo_pathpartargs']
                        + ['{}={}'.format(name,
                                          _percent_encode(_json.dumps(value)))
                           for name, value in self._echo_args_args.items()])

    @property
    def _echo_variadic_ordered_pathpartargs_path(self):
        return '&'.join(['echo_variadic_pathpartargs']
                        + ['{}={}'.format(name,
                                          _percent_encode(_json.dumps(value)))
                           for name, value in self._echo_args_args.items()])


# echo string arg tests -------------------------------------------------------


class _TestEchoStringResourceArgMixin(object):

    __metaclass__ = _abc.ABCMeta

    def test_get_arg_allvalues(self):
        self._test_request_arg_allvalues('get')

    def test_post_arg_allvalues(self):
        self._test_request_arg_allvalues('post')

    def test_postget_arg_allvalues(self):
        self._test_request_arg_allvalues('postget')

    def _argjson(self, value):
        return _json.dumps(value)

    @_abc.abstractmethod
    def _path(self, value):
        pass

    def _request_arg(self, method, string, **kwargs):
        return self.request(method, self._path(string),
                            argtypes=self._argtypes, **kwargs)


class _TestEchoUnquotedStringResourceArgMixin(_TestEchoStringResourceArgMixin):

    __metaclass__ = _abc.ABCMeta

    def _argjson(self, value):
        return value

    @property
    def _argvalues(self):
        return (value
                for value
                in super(_TestEchoUnquotedStringResourceArgMixin, self)
                    ._argvalues
                if not self._json_valid(value))

    def _json_valid(self, json):
        try:
            _json.loads(json)
        except ValueError:
            return False
        else:
            return True


class TestEchoStringPathArg(_TestEchoStringResourceArgMixin,
                            _echo_tests_core.TestEchoStringArg):
    def _path(self, string):
        return '/'.join(('echo_string_patharg', self._argjson(string)))


class TestEchoStringPathPartArg(_TestEchoStringResourceArgMixin,
                                _echo_tests_core.TestEchoStringArg):
    def _path(self, string):
        return u'echo_string_pathpartarg&string={}'\
                .format(self._argjson(string))


class TestEchoUnquotedStringPathArg(_TestEchoUnquotedStringResourceArgMixin,
                                    TestEchoStringPathArg,
                                    _echo_tests_core.TestEchoStringArg):
    pass


class TestEchoUnquotedStringPathPartArg\
       (_TestEchoUnquotedStringResourceArgMixin, TestEchoStringPathPartArg,
        _echo_tests_core.TestEchoStringArg):
    pass


# CORS tests ------------------------------------------------------------------


class TestEchoPathArgsCorsActualWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin, _testbedtest.TestCorsActual,
           TestEchoPathArgs):
    pass


class TestEchoPathArgsCorsActualWithUntrustedOrigin\
          (_echo_tests_core.TestEchoArgsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsActual, TestEchoPathArgs):
    pass


class TestEchoPathArgsCorsPreflightWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin,
           _testbedtest.TestCorsPreflight, TestEchoPathArgs):
    def assert_echo_args_response(self, response):
        self.assert_cors_preflight_accepted_response(response)


class TestEchoPathArgsCorsPreflightWithUntrustedOrigin\
          (_echo_tests_core.TestEchoArgsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsPreflight, TestEchoPathArgs):
    pass


class TestEchoPathPartArgsCorsActualWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin, _testbedtest.TestCorsActual,
           TestEchoPathPartArgs):
    pass


class TestEchoPathPartArgsCorsActualWithUntrustedOrigin\
          (_echo_tests_core.TestEchoArgsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsActual, TestEchoPathPartArgs):
    pass


class TestEchoPathPartArgsCorsPreflightWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin,
           _testbedtest.TestCorsPreflight, TestEchoPathPartArgs):
    def assert_echo_args_response(self, response):
        self.assert_cors_preflight_accepted_response(response)


class TestEchoPathPartArgsCorsPreflightWithUntrustedOrigin\
          (_echo_tests_core.TestEchoArgsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsPreflight, TestEchoPathPartArgs):
    pass


if __name__ == '__main__':
    _logging.basicConfig()
    _unittest.main()
