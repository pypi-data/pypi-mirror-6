""":mod:`Cross-origin resource sharing <testbed._cors>` testing."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import abc as _abc

from spruce.collections import frozenuset as _frozenuset

import testbed as _testbed
from . import _core as _testbedtest_core


class TestCors(_testbedtest_core.TestTestbed):

    __metaclass__ = _abc.ABCMeta

    @_abc.abstractproperty
    def cors_origin(self):
        pass

    @_abc.abstractproperty
    def expect_cors_origin_allowed(self):
        pass

    @property
    def webservice_path(self):
        return '/cors' + super(TestCors, self).webservice_path


class TestCorsActual(TestCors):

    __metaclass__ = _abc.ABCMeta

    def request(self, *args, **kwargs):
        return super(TestCorsActual, self).request(*args,
                                                   origin=self.cors_origin,
                                                   **kwargs)


class TestCorsPreflight(TestCors):

    __metaclass__ = _abc.ABCMeta

    def assert_cors_preflight_accepted_response(self, response, **kwargs):

        super(TestCorsPreflight, self)\
         .assert_cors_preflight_accepted_response(response, **kwargs)

        response_allowed_origins_header = \
            response.headers['Access-Control-Allow-Origin']
        response_allowed_origins = \
            _frozenuset('*' if response_allowed_origins_header == '*'
                            else (token.strip()
                                  for token
                                  in response_allowed_origins_header
                                      .split(',')))
        self.assertIn(self.cors_origin, response_allowed_origins)

    def request(self, method, resource, args=None, *args_, **kwargs):
        return super(TestCorsPreflight, self)\
                .request_cors_preflight(method, resource, *args_,
                                        origin=self.cors_origin,
                                        **kwargs)


class TestCorsWithTrustedOrigin(TestCors):

    @property
    def cors_origin(self):
        return _testbed.TRUSTED_ORIGIN

    @property
    def expect_cors_origin_allowed(self):
        return True


class TestCorsWithUntrustedOrigin(TestCors):

    @property
    def cors_origin(self):
        return _testbed.UNTRUSTED_ORIGIN

    @property
    def expect_cors_origin_allowed(self):
        return False
