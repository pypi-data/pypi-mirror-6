from django.db import models

class SetField(models.TextField, metaclass=models.SubfieldBase):
    description = "A field as a set."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(HandField, self).deconstruct()
        return name, path, args, kwargs

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, set):
            return value
        else: 
            return {item.strip(' &') for item in value.split(',')}

    def get_prep_value(self, value):
        return ", ".join([item.strip(" &'").strip('"') for item in str(value).lstrip('{').rstrip('}').split(',')])
