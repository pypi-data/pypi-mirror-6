import uuid

from whs.commons.abc.type_registry import TypeRegistry
from whs.commons.abc.dict_protocol import DictProtocol


class Serializable(DictProtocol):
    '''
    Objects inheriting from this class can be serialized, meaning "turned into 
    dict", so that they can be later casted to JSON, etc.
    Class needs to be registerd in TypeRegistry.
    '''
    def __init__(self):
        '''
        Inject unique ID (UUID v.4), type (according to TypeRegistry), and model
        version (also, according to TypeRegistry) to newly created instance.
        '''
        type_registry = TypeRegistry()
        self.uuid = str(uuid.uuid4())
        self.__type__ = type_registry.type(type(self))
        self.__model_version__ = type_registry.version(self.__type__)

    @property
    def fields(self):
        '''
        Return important fields - meaning these declared in @validable decorator
        (if class is decorated) or these that names don't start with underscore
        and aren't callable.
        '''
        if hasattr(type(self), "_needed_fields"):
            self.validate()
            fields = type(self)._needed_fields + ["uuid", "__type__", "__model_version__"]
        else:
            fields = [
                field
                for field in dir(self)
                if not field=="fields" and not field.startswith("_") and not hasattr(getattr(self, field), "__call__")
            ] + ["uuid", "__type__", "__model_version__"]
        return list(set(fields))

    def serialize(self):
        '''
        Turn this instance to dict.

        You really should use serialize function instead if this method.
        '''
        out = {}
        fields = self.fields
        for field in fields:
            out[field] = serialize(getattr(self, field))
        return out


def serialize(obj):
    '''
    Serialize object obj to JSON/BSON-compliant dict.
    '''
    if isinstance(obj, Serializable):
        return obj.serialize()
    elif isinstance(obj, (list, tuple)):
        return list(map(serialize, obj))
    elif isinstance(obj, set):
        return set(map(serialize, obj))
    elif isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[k] = serialize(v)
        return out
    return obj
