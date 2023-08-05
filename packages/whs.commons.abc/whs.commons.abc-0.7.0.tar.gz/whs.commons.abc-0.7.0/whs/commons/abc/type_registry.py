'''
This module introduces "type" abstraction.
Type is description of data, pointing to its intended usage, but without
implementation dependency.

For example, we can have type "TextDocument" which (at given stage of app
development) may be represented as class PlainTextDocument. Say we store
serialized PlainTextDocuments in some DB. If serialized with this package,
it will be represented as JSON with added __type__ and __model_version__ fields.

Some time later we may need some formatting in text documents. We create class
FormattedTextDocument - but it still represents the same type - TextDocument, but
with higher model version.

As long as we use PlainTextDocument, we keep entry:
"TextDocument": {
    "class" "some.package.PlainTextDocument",
    "version": "0.5"
}
in the regsitry file (0.5 is just an example). At the moment of switching to
FormattedTextDocument, we change entry above to:
"TextDocument": {
    "class" "other.pkg.FormattedTextDocument",
    "version": "0.7.5"
}
Now DB mediators can validate type of stored data (check whether given collection
or table keeps right type) and their version (because TypeRegistry provides
dynamic version inspection, mediators may decide to load only those objects which
version matches registered types version).

Main usage:
    TypeRegistry.load(somepath)
at somepath should be json with structure:
{
    type: {
        "class": qualified class name*,
        "version": well... types version
    },
    another_type: {
        ...
    },
    ...
}

* if class is in module which is ran as script, registry will find this out and
use proper module name, which is "__main__".

Thanks to that, (de)serialization can perform model versioning, and also we can
bind types of objects with their class representation.

Data is stored in named tuples, so you cannot change existing binding any other
way, then by reloading binding file.
'''
import importlib

import json
import os
import sys
from whs.commons.patterns.singleton import Singleton
from collections import namedtuple

TypeTuple = namedtuple("TypeTuple", ['cls', 'version'])

class AbstractView:
    '''
    Abstract marking class for views.
    You shouldn't inherit from this by yourself.
    '''
    pass

def View(field):
    '''
    Generate view class for given field.
    View(field)(dict) will return dict-like object which will bind calls (setters
    and getters of items) for v to dict[v].field
    '''
    
    def __init__(self, src):
        self.src = src

    def __getitem__(self, item):
        return getattr(self.src[item], field)

    def __contains__(self, item):
        return item in self.src

    def __iter__(self):
        return iter(self.src)

    def __len__(self):
        return len(self.src)

    out = type(field[0].upper()+field[1:]+"View", (AbstractView, ), {
        "__init__": __init__,
        "__getitem__": __getitem__,
        "__contains__": __contains__,
        "__iter__": __iter__,
        "__len__": __len__
    })
    return out

class TypeRegistry(Singleton, dict):
    '''
    Singleton dict keeping mappings (type -> TypeTuple(cls=class representing type,
                                                        version=types version)
    
    Methods returning bindings (class for type, version for type, etc) may
    raise KeyErrors.
    '''
    def __init__(self):
        if not self._initialized:
            self._class_view = None
            self._version_view = None
            self._initialized = True

    def load(self, path):
        '''
        Add or update fields of instance according to file from given path.
        '''
        with open(path) as f:
            entries = json.load(f)
        for k, v in entries.items():
            qualname = v['class']
            split = qualname.split('.')
            pkg = '.'.join(split[:-1])
            if pkg+".py" == os.path.split(sys.argv[0])[1]:
                pkg = '__main__'
            module = importlib.import_module(pkg)
            cls = getattr(module, split[-1])
            self[k] = TypeTuple(cls=cls, version=v['version'])

    def version(self, type=None, cls=None):
        '''
        Return version of given type or class.
        If both arguments are provided, returns version of type.
        '''
        if (cls or type) is None:
            raise IndexError("Neither class nor type specified!")
        if not (cls and type) is None:
            if self[type].cls==cls:
                pass
            raise LookupError("Class %r is not bound with type %r!" % (cls, type))
        if not type is None:
            return self[type].version
        for t, tup in self.items():
            if tup.cls == cls:
                return tup.version()
        raise KeyError("Class %r is not registered!" % cls)


    def class_(self, type):
        '''
        Return class registered to represent given type.
        '''
        return self[type].cls

    def type(self, cls):
        '''
        Return type for given class.
        '''
        for t, tup in self.items():
            if tup.cls==cls:
                return t
        raise KeyError("Class %r is not registered!" % cls)

    def classes(self):
        '''
        Return classes view (read-only dict-like object mapping types to classes).
        '''
        if self._class_view is None:
            self._class_view = View("cls")(self)
        return self._class_view

    def versions(self):
        '''
        Return versions view (read-only dict-like object mapping types to versions).
        '''
        if self._version_view is None:
            self._version_view = View("version")(self)
        return self._version_view

