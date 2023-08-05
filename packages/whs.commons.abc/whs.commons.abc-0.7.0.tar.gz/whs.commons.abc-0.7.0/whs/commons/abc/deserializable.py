from whs.commons.abc.type_registry import TypeRegistry


class Deserializable:
    '''
    Objects inheriting from this class can be reconstructed from any 
    JSON/BSON-compliant dict if there is "__type__" item.
    self['__type__'] has to be registered in TypeRegistry.
    '''
    def deserialize(self, repr_dict):
        '''
        Recursively inject values from argument to this instance.

        You really should use deserialize function instead of this method.
        '''
        # we need to go through keys in reverse order
        for k in reversed(sorted(repr_dict.keys())):
        # so type will come before args
        # because we dynamically generate lookup table for
        # args depending on type
            v = repr_dict[k]
            if not k.startswith("_"):
                setattr(self, k, deserialize(v, k, self.get_lookup()))
        return self

    def inject(self, to_inject):
        '''
        Set each field from to_inject.keys() to according to_inject value.
        It is similiar to deserialize(to_inject), but is not recursive.
        '''
        for k, v in to_inject.items():
            setattr(self, k, v)
        return self

    def get_lookup(self):
        '''
        You should override this; it should be mapping (field name -> field class)
        '''
        return {}

def deserialize(serialized, key=None, lookup_table=None):
    '''
    Deserialize serialized to object of class lookup_table[key].
    If key is None, we try to use serialized['__type__'].
    If lookup_table is None, we try to use TypeRegistry().classes() view.
    '''
    if key is None:
        key = serialized['__type__']
    if lookup_table is None:
        lookup_table = TypeRegistry().classes()
    if isinstance(serialized, (list, tuple)):
        return list(map(lambda x: deserialize(x, key, lookup_table), serialized))
    elif isinstance(serialized, set):
        return set(map(lambda x: deserialize(x, key, lookup_table), serialized))
    elif key in lookup_table:
        clazz = lookup_table[key]
        obj = clazz()
        if isinstance(serialized, clazz):
            return serialized
        if isinstance(obj, Deserializable):
            return obj.deserialize(serialized)
        raise TypeError("Type specified, but is not deserializable!")
    elif isinstance(serialized, dict):
        out = {}
        for k, v in serialized.items():
            out[k] = deserialize(serialized[k], k, lookup_table)
        return out
    return serialized

