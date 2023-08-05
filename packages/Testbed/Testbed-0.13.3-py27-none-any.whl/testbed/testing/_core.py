"""Testing core."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import abc as _abc

import bedframe as _bedframe
import bedframe.testing as _bedtest

import testbed as _testbed


class TestTestbed(_bedtest.WebServiceTestCase):

    __metaclass__ = _abc.ABCMeta

    @property
    def webservice_auth_realm_base(self):
        return 'testbed'

    def _create_webservice(self):
        return _testbed.TestbedService('tornado-wsgi',
                                       uris=('http://localhost:8080',),
                                       debug_flags=_bedframe.DEBUG_FULL)
