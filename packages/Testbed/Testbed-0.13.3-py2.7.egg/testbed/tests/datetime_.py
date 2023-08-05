#!/usr/bin/env python

""":mod:`Date and time <testbed.resources._datetime>` tests."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import csv as _csv
from datetime import datetime as _datetime, timedelta as _timedelta
import re as _re
from StringIO import StringIO as _StringIO
import unittest as _unittest

import bedframe.webtypes as _webtypes
import napper as _napper
import pytz as _tz
import spruce.datetime as _c_datetime
import spruce.http.status as _http_status
import spruce.logging as _logging

import testbed.testing as _testbedtest


class TestDatetime(_testbedtest.TestTestbed):

    def assert_difference_response(self, response):
        self.assert_return_response(response)
        difference = _napper.extract_retval(response,
                                            self._difference_returntype)
        self.assertEqual(difference, self._difference_expected_value)

    def assert_echo_response(self, response):
        self.assert_return_response(response)
        echo_dt = _napper.extract_retval(response, self._echo_returntype)
        self.assertEqual(echo_dt, self._echo_expected_value)

    def assert_echo_response_as_csv(self, response):
        self.assert_return_response(response, contenttype='text/csv')
        echo_dt = self._extract_echo_retval_from_csv(response)
        self.assertEqual(echo_dt, self._echo_expected_value)

    def assert_echo_valueerror_response(self, response):
        self.assert_exc_response(response,
                                 status=_http_status.BAD_REQUEST,
                                 class_def_module='bedframe._exc',
                                 name='ArgPrimValueError',
                                 message_pattern=
                                     'invalid \'dt\' primitive.*month must be'
                                      ' in 1..12')

    def assert_echo_valueerror_response_as_csv(self, response):
        self.assert_response_with_status(response, _http_status.NOT_ACCEPTABLE)

    def assert_now_response(self, response, before, after):
        self.assert_return_response(response)
        now = _napper.extract_retval(response, self._now_returntype)
        self.assertGreaterEqual(now, before)
        self.assertLessEqual(now, after)

    def assert_sum_response(self, response):
        self.assert_return_response(response)
        sum_ = _napper.extract_retval(response, self._sum_returntype)
        self.assertEqual(sum_, self._sum_expected_value)

    def test_get_difference(self):
        response = self.request('get', self._difference_path,
                                self._difference_args,
                                argtypes=self._difference_argtypes)
        self.assert_difference_response(response)

    def test_get_echo(self):
        response = self.request('get', self._echo_path, self._echo_args,
                                argtypes=self._echo_argtypes)
        self.assert_echo_response(response)

    def test_get_echo_as_application(self):
        response = self.request('get', self._echo_path, self._echo_args,
                                argtypes=self._echo_argtypes,
                                accept_mediaranges=('application/*',))
        self.assert_echo_response(response)

    def test_get_echo_as_application_or_csv(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_args,
                                argtypes=self._echo_argtypes,
                                accept_mediaranges=('application/*',
                                                    'text/csv'))
        self.assert_echo_response(response)

    def test_get_echo_as_application_q05_or_csv(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_args,
                                argtypes=self._echo_argtypes,
                                accept_mediaranges=('application/*; q=0.5',
                                                    'text/csv'))
        self.assert_echo_response_as_csv(response)

    def test_get_echo_as_csv_or_application(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_args,
                                argtypes=self._echo_argtypes,
                                accept_mediaranges=('text/csv',
                                                    'application/*'))
        self.assert_echo_response_as_csv(response)

    def test_get_echo_as_csv_or_json(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_args,
                                argtypes=self._echo_argtypes,
                                accept_mediaranges=('text/csv',
                                                    'application/json'))
        self.assert_echo_response_as_csv(response)

    def test_get_echo_as_csv_q05_or_application(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_args,
                                argtypes=self._echo_argtypes,
                                accept_mediaranges=('text/csv; q=0.5',
                                                    'application/*'))
        self.assert_echo_response(response)

    def test_get_echo_as_csv_q05_or_json(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_args,
                                argtypes=self._echo_argtypes,
                                accept_mediaranges=('text/csv; q=0.5',
                                                    'application/json'))
        self.assert_echo_response(response)

    def test_get_echo_as_json_or_csv(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_args,
                                argtypes=self._echo_argtypes,
                                accept_mediaranges=('application/json',
                                                    'text/csv'))
        self.assert_echo_response(response)

    def test_get_echo_as_json_q05_or_csv(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_args,
                                argtypes=self._echo_argtypes,
                                accept_mediaranges=('application/json; q=0.5',
                                                    'text/csv'))
        self.assert_echo_response_as_csv(response)

    def test_get_echo_valueerror(self):
        response = self.request('get', self._echo_path,
                                self._echo_valueerror_args,
                                argtypes=self._echo_valueerror_argtypes)
        self.assert_echo_valueerror_response(response)

    def test_get_echo_valueerror_as_csv(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_valueerror_args,
                                argtypes=self._echo_valueerror_argtypes,
                                accept_mediaranges=('text/csv',))
        self.assert_echo_valueerror_response_as_csv(response)

    def test_get_echo_valueerror_as_csv_or_json(self):
        response = self.request('get',
                                self._echo_path,
                                self._echo_valueerror_args,
                                argtypes=self._echo_valueerror_argtypes,
                                accept_mediaranges=('text/csv',
                                                    'application/json'))
        self.assert_echo_valueerror_response(response)

    def test_get_now(self):
        before = _c_datetime.now()
        response = self.request('get', self._now_path)
        after = _c_datetime.now()
        self.assert_now_response(response, before=before, after=after)

    def test_get_sum(self):
        response = self.request('get', self._sum_path, self._sum_args,
                                argtypes=self._sum_argtypes)
        self.assert_sum_response(response)

    def test_postget_difference_with_queryargs(self):
        response = self.request('postget',
                                self._difference_path,
                                self._difference_args,
                                argtypes=self._difference_argtypes,
                                args_as='query')
        self.assert_difference_response(response)

    def test_postget_difference_with_bodyargs(self):
        response = self.request('postget',
                                self._difference_path,
                                self._difference_args,
                                argtypes=self._difference_argtypes,
                                args_as='body')
        self.assert_difference_response(response)

    def test_postget_echo_with_queryargs(self):
        response = self.request('postget', self._echo_path, self._echo_args,
                                argtypes=self._echo_argtypes,
                                args_as='query')
        self.assert_echo_response(response)

    def test_postget_echo_with_bodyargs(self):
        response = self.request('postget', self._echo_path, self._echo_args,
                                argtypes=self._echo_argtypes,
                                args_as='body')
        self.assert_echo_response(response)

    def test_postget_now(self):
        before = _c_datetime.now()
        response = self.request('postget', self._now_path)
        after = _c_datetime.now()
        self.assert_now_response(response, before=before, after=after)

    def test_postget_sum_with_bodyargs(self):
        response = self.request('postget', self._sum_path, self._sum_args,
                                argtypes=self._sum_argtypes, args_as='body')
        self.assert_sum_response(response)

    def test_postget_sum_with_queryargs(self):
        response = self.request('postget', self._sum_path, self._sum_args,
                                argtypes=self._sum_argtypes, args_as='query')
        self.assert_sum_response(response)

    @property
    def webservice_path(self):
        return '/datetime'

    @property
    def webservice_probe_path(self):
        return self._now_path

    def _assert_return_response_as_csv(self, response):
        pass

    @property
    def _difference_args(self):
        return {'start': _datetime(2000, 1, 1, tzinfo=_tz.UTC),
                'end': _datetime(2001, 2, 3, 4, 5, 6, 7,
                                 tzinfo=_tz.FixedOffset(8 * 60 + 9))}

    @property
    def _difference_argtypes(self):
        return {'start': _webtypes.datetime, 'end': _webtypes.datetime}

    @property
    def _difference_expected_value(self):
        return self._difference_args['end'] - self._difference_args['start']

    @property
    def _difference_path(self):
        return 'difference'

    @property
    def _difference_returntype(self):
        return _webtypes.timedelta

    @property
    def _echo_args(self):
        return {'dt': _datetime(2001, 2, 3, 4, 5, 6, 7,
                                tzinfo=_tz.FixedOffset(8 * 60 + 9))}

    @property
    def _echo_argtypes(self):
        return {'dt': _webtypes.datetime}

    @property
    def _echo_expected_value(self):
        return self._echo_args['dt']

    @property
    def _echo_path(self):
        return 'echo'

    @property
    def _echo_returntype(self):
        return _webtypes.datetime

    @property
    def _echo_valueerror_args(self):
        return {'dt': '2001-13-03 04:05:06.000007 -08'}

    @property
    def _echo_valueerror_argtypes(self):
        return {'dt': _webtypes.unicode}

    def _extract_echo_retval_from_csv(self, response):

        strio = _StringIO(response.text)
        reader = _csv.reader(strio)
        year_str, month_str, day_str, hour_str, minute_str, second_str, \
         microsecond_str, tz_str = \
            reader.next()
        with self.assertRaises(StopIteration):
            reader.next()

        year = int(year_str)
        month = int(month_str)
        day = int(day_str)
        hour = int(hour_str or 0)
        minute = int(minute_str or 0)
        second = int(second_str or 0)
        microsecond = int(microsecond_str or 0)

        tz_match = _re.match(r'(?P<tz_sign>[-+])(?P<tz_hours>\d\d)'
                              r'(?P<tz_minutes>\d\d)?',
                             tz_str)
        if tz_match:
            tz_sign = tz_match.group('tz_sign')
            tz_hours = int(tz_sign + tz_match.group('tz_hours'))
            tz_minutes = int(tz_sign + (tz_match.group('tz_minutes') or '0'))
            tz_minutes += tz_hours * 60
            tzinfo = _tz.FixedOffset(tz_minutes)
        else:
            tzinfo = _tz.UTC

        return _datetime(year, month, day, hour, minute, second, microsecond,
                         tzinfo)

    @property
    def _now_path(self):
        return 'now'

    @property
    def _now_returntype(self):
        return _webtypes.datetime

    @property
    def _sum_args(self):
        return {'start': _datetime(2000, 1, 1, tzinfo=_tz.FixedOffset(30)),
                'offset': _timedelta(days=399, hours=4, minutes=5, seconds=6,
                                     microseconds=7)}

    @property
    def _sum_argtypes(self):
        return {'start': _webtypes.datetime, 'offset': _webtypes.timedelta}

    @property
    def _sum_expected_value(self):
        return self._sum_args['start'] + self._sum_args['offset']

    @property
    def _sum_path(self):
        return 'sum'

    @property
    def _sum_returntype(self):
        return _webtypes.datetime

TestDatetime._assert_return_response_meth_by_contenttype['text/csv'] = \
    TestDatetime._assert_return_response_as_csv


if __name__ == '__main__':
    _logging.basicConfig()
    _unittest.main()
