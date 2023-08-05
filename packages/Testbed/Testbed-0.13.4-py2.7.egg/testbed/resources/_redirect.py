"""Exception-triggering resources."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import bedframe as _bedframe
import bedframe.webtypes as _webtypes


class EntityChoiceRedirection(_bedframe.WebResource):

    @_bedframe.webmethod(locs=_webtypes.list(_webtypes.unicode),
                         preferred_loc=_webtypes.unicode)
    def __init__(self, locs, preferred_loc):
        self._locs = locs
        self._preferred_loc = preferred_loc

    @_bedframe.webmethod()
    def get(self):
        raise _bedframe.EntityChoiceRedirection(self.locs,
                                                preferred_loc=
                                                    self.preferred_loc)

    @property
    def locs(self):
        return self._locs

    @_bedframe.webmethod()
    def post(self):
        raise _bedframe.EntityChoiceRedirection(self.locs,
                                                preferred_loc=
                                                    self.preferred_loc)

    @property
    def preferred_loc(self):
        return self._preferred_loc


class SingleLocationRedirection(_bedframe.WebResource):

    @_bedframe.webmethod(loc=_webtypes.unicode)
    def __init__(self, loc):
        self._loc = loc

    @property
    def loc(self):
        return self._loc


class PermanentRedirection(SingleLocationRedirection):

    @_bedframe.webmethod()
    def get(self):
        raise _bedframe.PermanentRedirection(self.loc)

    @_bedframe.webmethod()
    def post(self):
        raise _bedframe.PermanentRedirection(self.loc)


class ProxyRedirection(SingleLocationRedirection):

    @_bedframe.webmethod()
    def get(self):
        raise _bedframe.ProxyRedirection(self.loc)

    @_bedframe.webmethod()
    def post(self):
        raise _bedframe.ProxyRedirection(self.loc)


class ResponseRedirection(SingleLocationRedirection):

    @_bedframe.webmethod()
    def get(self):
        raise _bedframe.ResponseRedirection(self.loc)

    @_bedframe.webmethod()
    def post(self):
        raise _bedframe.ResponseRedirection(self.loc)


class TemporaryRedirection(SingleLocationRedirection):

    @_bedframe.webmethod()
    def get(self):
        raise _bedframe.TemporaryRedirection(self.loc)

    @_bedframe.webmethod()
    def post(self):
        raise _bedframe.TemporaryRedirection(self.loc)
