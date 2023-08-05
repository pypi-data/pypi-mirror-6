#!/usr/bin/env python

"""Performance tests."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from time import time as _time
import threading as _threading
import unittest as _unittest

import bedframe.webtypes as _webtypes
import spruce.logging as _logging

import testbed.testing as _testbedtest


class TestPerformance(_testbedtest.TestTestbed):

    def test_get_noop_during_sleep(self):

        self._get_noop_finished_time = None
        self._get_sleep_finished_time = None

        get_sleep_thread = _threading.Thread(name='get sleep',
                                             target=self._get_sleep)
        get_noop_thread = _threading.Thread(name='get noop',
                                            target=self._get_noop)
        get_sleep_thread.start()
        get_noop_thread.start()
        get_sleep_thread.join()
        get_noop_thread.join()

        self.assertIsNot(self._get_noop_finished_time, None)
        self.assertIsNot(self._get_sleep_finished_time, None)
        self.assertLess(self._get_noop_finished_time,
                        self._get_sleep_finished_time)

    @property
    def webservice_path(self):
        return '/performance'

    @property
    def webservice_probe_path(self):
        return self._noop_path

    def _get_noop(self):
        self.request('get', self._noop_path)
        self._get_noop_finished_time = _time()

    def _get_sleep(self):
        self.request('get', self._sleep_path, {'duration': 1.},
                     argtypes={'duration': _webtypes.float})
        self._get_sleep_finished_time = _time()

    @property
    def _noop_path(self):
        return 'noop'

    @property
    def _sleep_path(self):
        return 'sleep'


if __name__ == '__main__':
    _logging.basicConfig()
    _unittest.main()
