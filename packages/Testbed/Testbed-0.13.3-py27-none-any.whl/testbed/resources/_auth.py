"""Authentication testing resources."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import bedframe as _bedframe
import bedframe.auth as _bedframe_auth
import bedframe.webtypes as _webtypes


class Welcome(_bedframe.WebResource):

    @_bedframe.webmethod(auth_provisions=_webtypes.nonweb)
    def __init__(self, auth_provisions=_bedframe_auth.SECPROV_CLIENT_AUTH):
        super(Welcome, self).__init__()
        self._auth_provisions = auth_provisions

    @property
    def auth_provisions(self):
        return self._auth_provisions

    @_bedframe.webmethod(_webtypes.unicode)
    def get(self):
        self.ensure_auth()
        return 'Welcome, {}'.format(self.current_auth_info.user)
