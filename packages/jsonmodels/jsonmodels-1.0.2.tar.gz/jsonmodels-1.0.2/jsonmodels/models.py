"""Base models."""

from . import parsers
from .fields import BaseField


class BaseMetaclass(type):

    """Metaclass for models."""

    def __new__(cls, name, bases, attr):

        fields = {}
        for name, field in attr.items():
            if isinstance(field, BaseField):
                attr[name] = field.get_value_replacement()
                fields[name] = field
        attr['_fields'] = fields

        return super(BaseMetaclass, cls).__new__(cls, name, bases, attr)


class Base(object):

    """Base class for all models."""

    __metaclass__ = BaseMetaclass

    def __init__(self, **kwargs):
        self.populate(**kwargs)

    def populate(self, **kw):
        """Populate values to fields."""
        for name, value in kw.items():
            # Check for field, if absent, skip this values.
            try:
                field = self._fields[name]
            except KeyError:
                continue

            # Let field decide in what format this value should be in.
            parsed_value = field.parse_value(value)

            setattr(self, name, parsed_value)

    def get_field(self, name):
        """Get field associated with given name/attribute."""
        return self._fields[name]

    def validate(self):
        """Validate."""
        for name, field in self._fields.items():
            value = getattr(self, name)
            field.validate(name, value)

    def __iter__(self):
        for name, field in self._fields.items():
            value = getattr(self, name)
            yield name, value

    def to_struct(self):
        """Cast model to structure. Shortcut method."""
        return parsers.to_struct(self)

    def to_json_schema(self):
        """Cast model to JSON schema. Shortcut method."""
        return parsers.to_json_schema(self)
