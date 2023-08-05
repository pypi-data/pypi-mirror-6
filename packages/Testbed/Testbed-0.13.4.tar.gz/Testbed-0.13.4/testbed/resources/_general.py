"""General resources."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import bedframe as _bedframe


class NoOp(_bedframe.WebResource):

    @_bedframe.webmethod()
    def get(self):
        pass

    @_bedframe.webmethod()
    def post(self):
        pass
