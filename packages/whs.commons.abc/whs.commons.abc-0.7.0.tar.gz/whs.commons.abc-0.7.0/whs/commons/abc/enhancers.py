'''
This module provides some utilities for easier class creation (universal __str__,
 __repr__, __eq__, __hash__, etc).
'''

def extract_fields(obj):
    '''
    Do not use this by yourself.
    If you extend this module - this function extracts important fields.
    If class has that fields, it return instance.fields; else it retur\ns list
    of fields without these that names start with underscore or are methods.
    '''
    if hasattr(obj, "fields"):
        fields = obj.fields
    else:
        fields = []
        for field in dir(obj):
            if not field.startswith("_") and not hasattr(getattr(obj, field), "__call__"):
                fields.append(field)
    return fields

class Formatted:
    '''
    Adds universal __str__ and __repr__ methods; with little effort with 
    customizing constructor __str__ output can be evaluated to equivalent object.
    '''
    def __repr__(self):
        fields = extract_fields(self)
        fields = map(lambda x: x+"="+repr(getattr(self, x)), fields)
        return type(self).__name__ + "{"+ ("; ".join(fields)) +"| #="+str(hash(self))+ "}"

    def __str__(self):
        fields = extract_fields(self)
        fields = map(lambda x: x+"="+repr(getattr(self, x)), fields)
        return type(self).__name__ + "("+ (", ".join(fields)) + ")"

class Recognizable:
    '''
    Adds universal __eq__ and __hash__ methods.
        __eq__ checks each field identity (besides 'hidden', meaning
    'starting with _' and callable fields).
        __hash__ sums class names hash with hash of each field. If field is list
    or set, its hash is calculated by sum of its elements hashes (recursively);
    if field is dict, its value is calculated by summing products of keys hash
    and values hash (also recursively); all other types are assumed to be hashable.
    '''
    def __eq__(self, other):
        if other is None:
            return False
        for field in extract_fields(self):
            if not getattr(self, field) == getattr(other, field):
                return False
        return True

    def _partial_hash(self, obj):
        '''
        Do not use this, it is internal way od hashing unhashable types.
        Implementation is pretty straightforward, you should understand it
        without futher explanation.
        '''
        if isinstance(obj, (list, set)):
            return sum([self._partial_hash(el) for el in obj])
        elif isinstance(obj, dict):
            return sum([self._partial_hash(k)*self._partial_hash(v) for k, v in obj.items()])
        return hash(obj)

    def __hash__(self):
        out = hash(type(self).__name__)
        for field in extract_fields(self):
            out += self._partial_hash(field)*self._partial_hash(getattr(self, field))
        return out

def validatable(fields):
    '''
    Decorator for data classes.
    
    @validatable(["a", "b"])
    class A:
        pass

    adds methods validate() to class A, which will check, whether instance has
    attributes a and b
    '''
    def validate(self):
        for field in fields:
            if not hasattr(self, field):
                msg = "Field "+field+" is not defined!"
                raise AttributeError(msg)
        return self
    def decorator(cls):
        cls.validate = validate
        cls._needed_fields = fields
        return cls
    return decorator
