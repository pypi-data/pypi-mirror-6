#!/usr/bin/env python

""":mod:`Echo <testbed.resources._echo>` tests core."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import abc as _abc

import bedframe.webtypes as _webtypes
import napper as _napper
from spruce.pprint import indented as _indented

import testbed.testing as _testbedtest


class TestEcho(_testbedtest.TestTestbed):
    @property
    def webservice_path(self):
        return '/echo'


class TestEchoArgs(TestEcho):

    def assert_echo_args_response(self, response,
                                  contenttype='application/json', **kwargs):

        self.assert_return_response(response, contenttype=contenttype,
                                    **kwargs)

        contenttype_name, _, _ = contenttype.partition(';')
        try:
            meth = self._assert_echo_args_response_meth_by_contenttype\
                    [contenttype_name]
        except KeyError:
            supported_contenttypes = \
                self._assert_echo_args_response_meth_by_contenttype.keys()
            raise ValueError('unsupported response content type {!r}:'
                              ' expecting one of {}'
                              .format(contenttype, supported_contenttypes))
        meth(self, response)

    def _assert_echo_args_response_as_html(self, response):
        # FIXME: factor out this behavior into
        #     :meth:`assert_return_response_with_value_prim()` or something
        #     related
        html_tree = self._asserted_html_response_content_tree(response)
        retval_tree = html_tree.find('body//*[@class="retval"]')
        retval = self._echo_args_returntype.fromjson(retval_tree.text).native()
        self.assertEqual(retval, self._echo_args_args)

    def _assert_echo_args_response_as_json(self, response):
        args = _napper.extract_retval(response, self._echo_args_returntype)
        self.assertEqual(args, self._echo_args_args)

    _assert_echo_args_response_meth_by_contenttype = {}

    @property
    def _echo_args_args(self):
        return {'bool': True,
                'bytes': '\x00\x01\x02',
                'dict': {'a': 0, 'o': 1, 'e': 2, 'u': 3},
                'float': 1.234,
                'int': 5,
                'list': ['a', 'o', 'e', 'u'],
                'null': None,
                'unicode': u'aoeu',
                }

    @property
    def _echo_args_argtypes(self):
        return {'bool': _webtypes.bool,
                'bytes': _webtypes.bytes,
                'dict': _webtypes.dict(_webtypes.unicode, _webtypes.int),
                'float': _webtypes.float,
                'int': _webtypes.int,
                'list': _webtypes.list(_webtypes.unicode),
                'null': _webtypes.null,
                'unicode': _webtypes.unicode,
                }

    @property
    def _echo_args_returntype(self):
        return _webtypes.dict(_webtypes.unicode, _webtypes.primitive)

TestEchoArgs\
 ._assert_echo_args_response_meth_by_contenttype\
 .update({'application/json': TestEchoArgs._assert_echo_args_response_as_json,
          'text/html': TestEchoArgs._assert_echo_args_response_as_html})


class TestEchoStringArg(TestEcho):

    __metaclass__ = _abc.ABCMeta

    def assert_echo_stringarg_response(self, string, response,
                                       contenttype='application/json',
                                       **kwargs):

        if len(string) > 2 \
               and string.startswith('"') \
               and string.endswith('"'):
            string = string[1:-1]

        self.assert_return_response(response, contenttype=contenttype,
                                    **kwargs)

        contenttype_name, _, _ = contenttype.partition(';')
        try:
            meth = self._assert_echo_stringarg_response_meth_by_contenttype\
                    [contenttype_name]
        except KeyError:
            supported_contenttypes = \
                self._assert_echo_stringarg_response_meth_by_contenttype.keys()
            raise ValueError('unsupported response content type {!r}:'
                              ' expecting one of {}'
                              .format(contenttype, supported_contenttypes))
        meth(self, response, string)

    def _assert_echo_stringarg_response_as_html(self, response, string):
        # FIXME: factor out this behavior into
        #     :meth:`assert_return_response_with_value_prim()` or something
        #     related
        html_tree = self._asserted_html_response_content_tree(response)
        retval_tree = html_tree.find('body//*[@class="retval"]')
        retval = self._returntype.fromjson(retval_tree.text).native()
        self.assertEqual(retval, string)

    def _assert_echo_stringarg_response_as_json(self, response, string):
        args = _napper.extract_retval(response, self._returntype)
        self.assertEqual(args, string)

    _assert_echo_stringarg_response_meth_by_contenttype = {}

    @property
    def _argvalues(self):
        VALUES_KNOWN_BUGGY_IN_TORNADO = ('+', '.')
        VALUES_KNOWN_BUGGY_IN_UJSON = ('-',)
        VALUES_KNOWN_BUGGY = VALUES_KNOWN_BUGGY_IN_TORNADO \
                              + VALUES_KNOWN_BUGGY_IN_UJSON
        return (value
                for value
                in (u'', '')
                   + tuple(char for char in (unichr(ord_)
                                             for ord_ in range(0xff))
                           if char not in self.webservice.resources.seps)
                   + (u'aoeu', 'aoeu')
                   + (u'null', 'null', u'true', 'true', u'false', 'false',
                      u'nan', 'nan', u'inf', 'inf', u'-inf', '-inf', '0.a',
                      '-1.a', 'a.', 'a.b')
                if value not in VALUES_KNOWN_BUGGY)

    @property
    def _argtypes(self):
        return {'string': _webtypes.unicode}

    @_abc.abstractmethod
    def _request_arg(self, method, string):
        pass

    @property
    def _returntype(self):
        return _webtypes.unicode

    def _test_request_arg(self, method, string, contenttype='application/json',
                          **kwargs):
        self.assert_echo_stringarg_response(string,
                                            self._request_arg(method, string,
                                                              **kwargs),
                                            contenttype=contenttype)

    def _test_request_arg_allvalues(self, method, **kwargs):
        for string in self._argvalues:
            try:
                self._test_request_arg(method, string, **kwargs)
            except AssertionError as exc:
                self.fail('failed subtest for argument {!r}:\n{}'
                           .format(string, _indented(str(exc), size=2)))

TestEchoStringArg\
 ._assert_echo_stringarg_response_meth_by_contenttype\
 .update({'application/json':
              TestEchoStringArg._assert_echo_stringarg_response_as_json,
          'text/html':
              TestEchoStringArg._assert_echo_stringarg_response_as_html,
          })


class TestEchoArgsCorsWithUntrustedOriginMixin(object):
    def assert_echo_args_response(self, response, **kwargs):
        self.assert_cors_rejected_response(response,
                                           exc_name='CorsOriginForbidden',
                                           **kwargs)
