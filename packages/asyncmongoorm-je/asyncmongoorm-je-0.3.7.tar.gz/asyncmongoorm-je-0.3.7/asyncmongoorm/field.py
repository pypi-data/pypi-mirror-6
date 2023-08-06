# coding: utf-8
from datetime import datetime, date
from bson import ObjectId, Binary

class Field(object):
    
    def __init__(self, default=None, name=None, field_type=None, index=None):
        
        self.default = default
        self.field_type = field_type
        self.name = name
        self.index = self._clean_index(index)

    def _clean_index(self, index):
        allowed = ("dropDups", "sparse", "unique")
        def check(option):
            assert option in allowed, ("Unknown index option %s,"
                                  " allowed are %s" % (option, allowed))
        if isinstance(index, str):
            index = (index,)
        if isinstance(index, (list,tuple,set)):
            map(check, index)
            return tuple(set(index))
        return index

    def __get__(self, instance, owner):
        if not instance:
            return self
            
        value = instance._data.get(self.name)
        if value is None and self.default is not None:
            if callable(self.default):
                value = self.default()
            else:
                value = self.default
            setattr(instance, self.name, value)

        return value

    def _coerce(self, value):
        try:
            return self.field_type(value)
        except TypeError:
            raise(TypeError("type of %s must be %s" % (self.name, self.field_type)))
        except ValueError:
            raise(TypeError("type of %s must be %s" % (self.name, self.field_type)))

    def __set__(self, instance, value):
        # Attempt to coerce value to a field type
        if value is not None and not isinstance(value, self.field_type):
            value = self._coerce(value)

        # MongoDB doesnt allow to change _id
        if self.name != "_id":
            instance._changed_fields.add(self.name)

        current_value = instance._data.get(self.name)
        value_updated = value != current_value
        if value_updated:
            instance._data[self.name] = value

class StringField(Field):

    def __init__(self, *args, **kwargs):

        super(StringField, self).__init__(field_type=unicode, *args, **kwargs)
        
class IntegerField(Field):

    def __init__(self, *args, **kwargs):
        
        super(IntegerField, self).__init__(field_type=int, *args, **kwargs)

class DateTimeField(Field):

    def __init__(self, *args, **kwargs):
        
        super(DateTimeField, self).__init__(field_type=datetime, *args, **kwargs)

class DateField(Field):

    def __init__(self, *args, **kwargs):

        super(DateField, self).__init__(field_type=date, *args, **kwargs)

    def __get__(self, instance, owner):
        if not instance:
            return self

        value = instance._data.get(self.name)
        if value is None and self.default:
            if callable(self.default):
                value = self.default()
            else:
                value = self.default
            setattr(instance, self.name, value)

        return datetime(value.year, value.month, value.day)
    
class BooleanField(Field):

    def __init__(self, *args, **kwargs):

        super(BooleanField, self).__init__(field_type=bool, *args, **kwargs)

class FloatField(Field):

    def __init__(self, *args, **kwargs):

        super(FloatField, self).__init__(field_type=float, *args, **kwargs)

class ListField(Field):

    def __init__(self, *args, **kwargs):

        super(ListField, self).__init__(field_type=list, *args, **kwargs)

class ObjectField(Field):

    def __init__(self, *args, **kwargs):

        super(ObjectField, self).__init__(field_type=dict, *args, **kwargs)

class ObjectIdField(Field):

    def __init__(self, *args, **kwargs):

        super(ObjectIdField, self).__init__(field_type=ObjectId, *args, **kwargs)

class BinaryField(Field):
    def __init__(self, *args, **kwargs):

        super(BinaryField, self).__init__(field_type=Binary, *args, **kwargs)
