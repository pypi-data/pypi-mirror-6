"""Exception-triggering resources."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import exceptions as _exc

import bedframe as _bedframe


class RuntimeError(_bedframe.WebResource):

    @_bedframe.webmethod()
    def get(self):
        raise _exc.RuntimeError('this is an exceptionally expected exception')

    @_bedframe.webmethod()
    def post(self):
        raise _exc.RuntimeError('this is an exceptionally expected exception')
