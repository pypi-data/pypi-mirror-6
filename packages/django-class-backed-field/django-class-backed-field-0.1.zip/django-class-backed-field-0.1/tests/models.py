from django.db import models
from class_backed_field import fields


class ListFromString(object):
    def __init__(self, a_string):
        self.the_list = list(a_string)

class TestModel(models.Model):
    strings = fields.ClassBackedField(represents=ListFromString, db_value_generator=lambda x: "".join(x.the_list), max_length=255)
