from whs.commons.abc.deserializable import Deserializable
from whs.commons.abc.enhancers import Recognizable, Formatted
from whs.commons.abc.serializable import Serializable
from whs.commons.abc.session import Session


class DTO(Formatted, Recognizable, Serializable, Deserializable):
    '''
    Base class for Data Transfer Objects.
    Automatically adds uuid for instance and uuid of session in which instance 
    was created.
    It is (de)serializable, has universal __str__, __repr__, __eq__ and __hash__
    methods.
    By default, eval(str(x))==x (if x is instance of DTO).
    Class itself is unusable, you have to inherit from this and register new
    class in TypeRegistry (or register DTO class).
    '''
    def __init__(self, **kwargs):
        '''
        Initialize this instance as serializable, create unique ID (by UUID v.4),
        inject session id and copy passed args as instance fields.
        '''
        Serializable.__init__(self)
        self.creation_session_id = Session().uuid
        for k, v in kwargs.items():
            self[k] = v

    @property
    def fields(self):
        '''
        This field/property should contain list of fields that should be
        (de)serialized.
        '''
        return list(set(Serializable.fields.fget(self) + ["creation_session_id"]))
