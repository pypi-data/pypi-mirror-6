class DictProtocol(dict):
    '''
    This class makes left and right expressions and statements equivalent
    (if a is instance of some subclass od this class):
    a.x             <=>         a['x']
    a.x = b         <=>         a['x'] = b
    hasattr(a, b)   <=>         b in a

    Note: this should be first superclass while creating new class; last line
    will work only, if b is added when new class is already subclass of this (so
    class-level attributes in other ancestor classes will be assigned in unified
    style).
    '''
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as e:
            dict.__getattribute__(self, item)
    def __setattr__(self, key, value):
        self[key] = value
    def __dir__(self):
        return list(self.keys()) + object.__dir__(self)
