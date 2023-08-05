"""Method arguments."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import __builtin__

import bedframe as _bedframe
import bedframe.webtypes as _webtypes


class EchoMethodArgs(_bedframe.WebResource):

    @_bedframe.webmethod(_webtypes.dict(_webtypes.unicode,
                                        _webtypes.primitive),
                         bool=_webtypes.bool,
                         bytes=_webtypes.bytes,
                         dict=_webtypes.dict(_webtypes.unicode,
                                             _webtypes.int),
                         float=_webtypes.float,
                         int=_webtypes.int,
                         list=_webtypes.list(_webtypes.unicode),
                         null=_webtypes.null,
                         unicode=_webtypes.unicode)
    def get(self, bool, bytes, dict, float, int, list, null, unicode):
        return __builtin__.dict(zip(('bool', 'bytes', 'dict', 'float', 'int',
                                     'list', 'null', 'unicode'),
                                    (bool, bytes, dict, float, int, list, null,
                                     unicode)))

    @_bedframe.webmethod(_webtypes.dict(_webtypes.unicode,
                                        _webtypes.primitive),
                         bool=_webtypes.bool,
                         bytes=_webtypes.bytes,
                         dict=_webtypes.dict(_webtypes.unicode,
                                             _webtypes.int),
                         float=_webtypes.float,
                         int=_webtypes.int,
                         list=_webtypes.list(_webtypes.unicode),
                         null=_webtypes.null,
                         unicode=_webtypes.unicode)
    def post(self, bool, bytes, dict, float, int, list, null, unicode):
        return __builtin__.dict(zip(('bool', 'bytes', 'dict', 'float', 'int',
                                     'list', 'null', 'unicode'),
                                    (bool, bytes, dict, float, int, list, null,
                                     unicode)))


class EchoStringMethodArg(_bedframe.WebResource):

    @_bedframe.webmethod(_webtypes.unicode, string=_webtypes.unicode)
    def get(self, string):
        return string

    @_bedframe.webmethod(_webtypes.unicode, string=_webtypes.unicode)
    def post(self, string):
        return string


class EchoVariadicMethodArgs(_bedframe.WebResource):

    @_bedframe.webmethod(_webtypes.dict(_webtypes.unicode,
                                        _webtypes.primitive),
                         bool=_webtypes.bool,
                         bytes=_webtypes.bytes,
                         dict=_webtypes.dict(_webtypes.unicode,
                                             _webtypes.int),
                         float=_webtypes.float,
                         int=_webtypes.int,
                         list=_webtypes.list(_webtypes.unicode),
                         null=_webtypes.null,
                         unicode=_webtypes.unicode)
    def get(self, **args):
        return args

    @_bedframe.webmethod(_webtypes.dict(_webtypes.unicode,
                                        _webtypes.primitive),
                         bool=_webtypes.bool,
                         bytes=_webtypes.bytes,
                         dict=_webtypes.dict(_webtypes.unicode,
                                             _webtypes.int),
                         float=_webtypes.float,
                         int=_webtypes.int,
                         list=_webtypes.list(_webtypes.unicode),
                         null=_webtypes.null,
                         unicode=_webtypes.unicode)
    def post(self, **args):
        return args
