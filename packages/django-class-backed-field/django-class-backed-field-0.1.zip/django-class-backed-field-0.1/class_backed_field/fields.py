from django.db import models
from django.utils.six import with_metaclass
from django.conf import settings
if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^class_backed_field\.fields\.ClassBackedField"])


id_lambda = lambda x: str(x.id)


class ClassRequiredException(Exception):
    pass


class CallableRequiredException(Exception):
    pass


class ClassBackedField(with_metaclass(models.SubfieldBase, models.CharField)):
    description = "Store a string in a database and creates an instance of a give class from it."

    def __init__(self, represents=None, db_value_generator=None, *args, **kwargs):
        """Represents is a class that you expect this field to be an instance of, db_value_generator is a callable that will generate the value you would like stored in the database form an instance (defauls to calling '.id' on the object)."""
        if represents is None:
            raise ClassRequiredException()
        self._represents = represents
        self._db_value_generator = db_value_generator
        kwargs['db_index'] = True
        super(ClassBackedField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, self._represents):
            return value
        return self._represents(value)

    def get_prep_value(self, value):
        if isinstance(value, self._represents):
            return self._db_value_generator(value)
        return value

    def run_validators(self, value):
        value = self.get_prep_value(value)
        return super(ClassBackedField, self).run_validators(value)

    def get_prep_lookup(self, lookup_type, value):
    # We only handle 'exact' and 'in'. All others are errors.
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)
