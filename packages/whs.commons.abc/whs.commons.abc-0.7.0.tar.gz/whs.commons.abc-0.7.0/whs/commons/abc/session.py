'''
This module provide universal Session management.

By default, it uses BaseSession for session representation, but you can register
 your own, by calling:
    Session.use(demanded class)
(it can also be used as class decorator) or assigning
    Session.cls = demanded class

After beginning session, you cannot change session class until session ends.

Custom session classes has to inherit from BaseSession.

To inspect actual session class, check value of Session.cls

If you want to extend session data, override methods at_begin() (called after
session.begin()), at_end() (called after session.end() but before cleaning) and
custom_clean() (called at the end of session.end(); it should set all custom
fields to None, 0, empty structure, etc).

Session objects always have following fields:
 - uuid: str (string version of uuid4 for given instance)
 - start_time: datetime (datetime in UTC indicating when session started)
 - end_time: datetime (as start_time, but is set in end() - if you want to use
        it, you need to override at_end(), because clean() removes it)
 - open: boolean  (indicating whether session is opened)

Instead of creating an instance by yourself, use Session() proxy, which will
create instance of proper class, check whether any other session is created,
will keep it as singleton, etc.
'''

import datetime
import uuid
from whs.commons.abc.enhancers import Recognizable, Formatted

NON_OVERRIDEN_METHODS = [
    'begin',
    'end',
    'clean'
]

class AbstractSession(Formatted, Recognizable):
    '''
    Root of session inherintance tree; defines user-API.
    '''
    def __init__(self):
        self.clean()

    def begin(self, **kwargs):
        self.start_time = datetime.datetime.utcnow()
        self.open=True
        self.uuid = str(uuid.uuid4())
        self.at_begin(**kwargs)

    def end(self, **kwargs):
        self.end_time = datetime.datetime.utcnow()
        self.at_end(**kwargs)
        uuid = self.uuid
        self.clean()
        return uuid


    def clean(self):
        self.open = False
        self.uuid = None
        self.start_time = None
        self.end_time = None
        self.custom_clean()


class MetaSession(type):
    '''
    Metaclass, ensuring that API of session will not be overriden.
    '''
    def __new__(cls, name, bases, namespace, **kwds):
        overlapping = list(set(NON_OVERRIDEN_METHODS) - set(namespace.keys()))
        if not len(overlapping) == len(NON_OVERRIDEN_METHODS):
            raise RuntimeError("Following methods cannot be overriden, but are: "+(", ".join(overlapping)))

        return type.__new__(cls, name, bases, namespace, **kwds)

class BaseSession(AbstractSession, metaclass=MetaSession):
    '''
    Basic implementation of session, injecting empty hooks.
    '''

    def at_begin(self):
        pass

    def at_end(self):
        pass

    def custom_clean(self):
        pass


class Session(BaseSession):
    '''
    Proxy class for session with class-registering utilities
    '''

    _session_class = BaseSession
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None or not type(cls._instance) == cls.get_cls():
            cls._instance = cls.get_cls()(*args, **kwargs)
        return cls._instance

    def __init__(self):
        pass

    # @property
    @classmethod
    def get_cls(cls):
        return Session._session_class

    # @cls.setter
    @classmethod
    def set_cls(cls, new_class):
        if Session._instance is not None and Session._instance.open:
            raise RuntimeError("Changing session class with opened session is not allowed!")
        if not issubclass(new_class, BaseSession):
            raise RuntimeError("Class %s is not subclass of %s, so it cannot be session class!" % (new_class, BaseSession))
        if not type(new_class) == MetaSession:
            raise RuntimeError("Class %s is not created with metaclass %s but with %s" % (new_class, MetaSession, type(new_class)))
        Session._session_class = new_class

    @classmethod
    def use(cls, clazz):
        Session.set_cls(clazz)
        return clazz
