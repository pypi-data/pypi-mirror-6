from .models import TestModel, ListFromString
from django.utils import unittest


class ModelFieldTests(unittest.TestCase):
    alpha = "abc"
    alternative_id = "25049"
    another_id = "289467"

    def tearDown(self):
        TestModel.objects.all().delete()

    def test_saving_field(self):
        obj = TestModel.objects.create(strings=self.alpha)
        self.assertTrue(obj.pk is not None)
        self.assertIsInstance(obj.strings, ListFromString)

    def test_retriving_field_by_data_value(self):
        obj = TestModel.objects.create(strings=self.alpha)
        obj2 = TestModel.objects.get(id=obj.id)
        self.assertIsInstance(obj2.strings, ListFromString)
        self.assertEqual(obj2.strings.the_list, obj.strings.the_list)

    def test_retriving_field_by_instance(self):
        obj = TestModel.objects.create(strings=self.alpha)
        TestModel.objects.create(strings=self.alternative_id)
        TestModel.objects.create(strings=self.another_id)
        list_from_string = ListFromString(self.alpha)
        result = TestModel.objects.get(strings=list_from_string)
        self.assertIsInstance(obj.strings, ListFromString)
        self.assertEqual(result.strings.the_list[-1], obj.strings.the_list[-1])
