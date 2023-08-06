import inspect
import types
import sys

__all__ = ('PathParam', 'QueryParam', 'BodyParam', 'FileParam')


class Param(object):
    required = True
    
    def __init__(self, value, default=None):
        self.value = value
        self.default = default


class PathParam(Param):
    pass


class QueryParam(Param):
    def __init__(self, *args, **kwargs):
        self.required = kwargs.pop('required', True)
        super(QueryParam, self).__init__(*args, **kwargs)


class DataParam(Param):
    pass


class FileParam(Param):
    pass


param_types = {}
for name, cls in inspect.getmembers(sys.modules[__name__]):
    if isinstance(cls, (types.TypeType, Param)):
        param_types[name] = cls