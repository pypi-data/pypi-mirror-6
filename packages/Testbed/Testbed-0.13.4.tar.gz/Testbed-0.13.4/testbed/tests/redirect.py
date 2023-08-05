#!/usr/bin/env python

""":mod:`Redirection <testbed.resources._redirect>` tests."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import json as _json
import unittest as _unittest
from urllib import quote as _percent_encode

import napper as _napper
import spruce.logging as _logging

import testbed.testing as _testbedtest


class TestRedirections(_testbedtest.TestTestbed):

    @property
    def webservice_path(self):
        return '/redirect'

    @property
    def webservice_probe_path(self):
        return self._redirect_path

    def _create_requests_session(self):
        return _napper.WebRequestSession(follow_redirects=False)


class TestResponseRedirection(TestRedirections):

    def test_get_response_redirect(self):
        response = self.request('get', self._redirect_path)
        self.assert_response_redirect_response(response,
                                               loc=self._redirect_loc)

    def test_get_response_redirect_as_html(self):
        response = self.request('get',
                                self._redirect_path,
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_response_redirect_response(response,
                                               loc=self._redirect_loc,
                                               contenttype='text/html')

    def test_post_response_redirect(self):
        response = self.request('post', self._redirect_path)
        self.assert_response_redirect_response(response,
                                               loc=self._redirect_loc)

    def test_post_response_redirect_as_html(self):
        response = self.request('post',
                                self._redirect_path,
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_response_redirect_response(response,
                                               loc=self._redirect_loc,
                                               contenttype='text/html')

    def test_postget_response_redirect(self):
        response = self.request('postget', self._redirect_path)
        self.assert_response_redirect_response(response,
                                               loc=self._redirect_loc)

    def test_postget_response_redirect_as_html(self):
        response = self.request('postget',
                                self._redirect_path,
                                accept_mediaranges=('text/html',
                                                    '*/*; q=0.01'))
        self.assert_response_redirect_response(response,
                                               loc=self._redirect_loc,
                                               contenttype='text/html')

    @property
    def _redirect_loc(self):
        return 'aoeu'

    @property
    def _redirect_path(self):
        return 'response;loc={}'\
                .format(_percent_encode(_json.dumps(self._redirect_loc),
                                        safe=''))


class _TestRedirectionsCorsWithUntrustedOriginMixin(object):
    def assert_response_redirect_response(self, response, **kwargs):
        kwargs_ = {}
        try:
            kwargs_['contenttype'] = kwargs['contenttype']
        except KeyError:
            pass
        self.assert_cors_rejected_response(response,
                                           exc_name='CorsOriginForbidden',
                                           **kwargs_)


class TestRedirectionsCorsActualWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin, _testbedtest.TestCorsActual,
           TestRedirections):
    pass


class TestRedirectionsCorsActualWithUntrustedOrigin\
          (_TestRedirectionsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsActual, TestRedirections):
    pass


class TestRedirectionsCorsPreflightWithTrustedOrigin\
          (_testbedtest.TestCorsWithTrustedOrigin,
           _testbedtest.TestCorsPreflight, TestRedirections):
    def assert_response_redirect_response(self, response, **kwargs):
        kwargs_ = {}
        try:
            kwargs_['contenttype'] = kwargs['contenttype']
        except KeyError:
            pass
        self.assert_cors_preflight_accepted_response(response, **kwargs_)


class TestRedirectionsCorsPreflightWithUntrustedOrigin\
          (_TestRedirectionsCorsWithUntrustedOriginMixin,
           _testbedtest.TestCorsWithUntrustedOrigin,
           _testbedtest.TestCorsPreflight, TestRedirections):
    pass


if __name__ == '__main__':
    _logging.basicConfig()
    _unittest.main()
