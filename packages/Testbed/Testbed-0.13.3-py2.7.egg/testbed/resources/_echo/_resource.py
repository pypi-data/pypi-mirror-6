"""Resource arguments."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import bedframe as _bedframe
import bedframe.webtypes as _webtypes


class EchoResourceArgs(_bedframe.WebResource):

    @_bedframe.webmethod(bool=_webtypes.bool,
                         bytes=_webtypes.bytes,
                         dict=_webtypes.dict(_webtypes.unicode,
                                             _webtypes.int),
                         float=_webtypes.float,
                         int=_webtypes.int,
                         list=_webtypes.list(_webtypes.unicode),
                         null=_webtypes.null,
                         unicode=_webtypes.unicode)
    def __init__(self, bool, bytes, dict, float, int, list, null, unicode,
                 **kwargs):
        super(EchoResourceArgs, self).__init__(**kwargs)
        self._bool = bool
        self._bytes = bytes
        self._dict = dict
        self._float = float
        self._int = int
        self._list = list
        self._null = null
        self._unicode = unicode

    @property
    def bool(self):
        return self._bool

    @property
    def bytes(self):
        return self._bytes

    @property
    def dict(self):
        return self._dict

    @property
    def float(self):
        return self._float

    @_bedframe.webmethod(_webtypes.dict(_webtypes.unicode,
                                        _webtypes.primitive))
    def get(self):
        return dict(zip(('bool', 'bytes', 'dict', 'float', 'int', 'list',
                         'null', 'unicode'),
                        (self.bool, self.bytes, self.dict, self.float,
                         self.int, self.list, self.null, self.unicode)))

    @property
    def int(self):
        return self._int

    @property
    def list(self):
        return self._list

    @property
    def null(self):
        return self._null

    @_bedframe.webmethod(_webtypes.dict(_webtypes.unicode,
                                        _webtypes.primitive))
    def post(self):
        return dict(zip(('bool', 'bytes', 'dict', 'float', 'int', 'list',
                         'null', 'unicode'),
                        (self.bool, self.bytes, self.dict, self.float,
                         self.int, self.list, self.null, self.unicode)))

    @property
    def unicode(self):
        return self._unicode


class EchoStringResourceArg(_bedframe.WebResource):

    @_bedframe.webmethod(string=_webtypes.unicode)
    def __init__(self, string):
        self._string = string

    @_bedframe.webmethod(_webtypes.unicode)
    def get(self):
        return self._string

    @_bedframe.webmethod(_webtypes.unicode)
    def post(self):
        return self._string

    @property
    def string(self):
        return self._string


class EchoVariadicResourceArgs(EchoResourceArgs):

    @_bedframe.webmethod(bool=_webtypes.bool,
                         bytes=_webtypes.bytes,
                         dict=_webtypes.dict(_webtypes.unicode,
                                             _webtypes.int),
                         float=_webtypes.float,
                         int=_webtypes.int,
                         list=_webtypes.list(_webtypes.unicode),
                         null=_webtypes.null,
                         unicode=_webtypes.unicode)
    def __init__(self, **args):
        for name, value in args.items():
            setattr(self, '_' + name, value)
