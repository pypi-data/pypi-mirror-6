from odin import exceptions
from odin.resources import create_resource_from_dict
from odin.fields import Field
from odin.validators import EMPTY_VALUES

__all__ = ('DictAs', 'ObjectAs', 'ArrayOf',)


class DictAs(Field):
    default_error_messages = {
        'invalid': "Must be a object of type ``%r``.",
    }

    def __init__(self, resource, **kwargs):
        try:
            resource._meta
        except AttributeError:
            raise TypeError("``%r`` is not a valid type for a related field." % resource)
        self.of = resource

        kwargs.setdefault('default', lambda: resource())
        super(DictAs, self).__init__(**kwargs)

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, self.of):
            return value
        if isinstance(value, dict):
            return create_resource_from_dict(value, self.of._meta.resource_name)
        msg = self.error_messages['invalid'] % self.of
        raise exceptions.ValidationError(msg)

    def validate(self, value):
        super(DictAs, self).validate(value)
        if value not in EMPTY_VALUES:
            value.full_clean()


class ObjectAs(DictAs):
    pass


class ArrayOf(DictAs):
    default_error_messages = {
        'invalid': "Must be a list of ``%r`` objects.",
        'null': "List cannot contain null entries.",
    }

    def __init__(self, resource, **kwargs):
        kwargs.setdefault('default', list)
        super(ArrayOf, self).__init__(resource, **kwargs)

    def _process_list(self, value_list, method):
        values = []
        errors = {}
        for idx, value in enumerate(value_list):
            error_key = str(idx)

            try:
                values.append(method(value))
            except exceptions.ValidationError as ve:
                errors[error_key] = ve.error_messages

        if errors:
            raise exceptions.ValidationError(errors)

        return values

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, list):
            super_to_python = super(ArrayOf, self).to_python

            def process(val):
                if val is None:
                    raise exceptions.ValidationError(self.error_messages['null'])
                return super_to_python(val)

            return self._process_list(value, process)
        msg = self.error_messages['invalid'] % self.of
        raise exceptions.ValidationError(msg)

    def validate(self, value):
        # Skip The direct super method and apply it to each list item.
        super(DictAs, self).validate(value)
        if value not in EMPTY_VALUES:
            super_validate = super(ArrayOf, self).validate
            self._process_list(value, super_validate)
