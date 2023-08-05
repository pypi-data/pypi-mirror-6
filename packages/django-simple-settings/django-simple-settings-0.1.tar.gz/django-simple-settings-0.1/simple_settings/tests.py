from django.test import TestCase
from django.db import connection
from django import conf

from .models import Settings
from .import settings


class SimpleSettingsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        # The test runner sets DEBUG to False. Set to True to enable SQL logging.
        setattr(conf.settings, 'DEBUG', True)

    def test_get(self):

        test_key = "test_get_key"
        test_value = "test_get_value"

        Settings.objects.create(key=test_key, value=test_value)

        self.assertEquals(settings.get(test_key), test_value)
        self.assertEquals(settings[test_key], test_value)

    def test_get_unknown_key(self):
        test_key = "test_get_unknown_settings_key"

        self.assertEquals(settings.get(test_key), None)
        try:
            self.assertEquals(settings[test_key], "test_get_unknown_settings")
        except KeyError:
            pass
        else:
            self.fail("Should throw KeyError exception")

    def test_boolean_key(self):
        test_key = "test_boolean_key"

        # test true
        Settings.objects.create(key=test_key, value="true", value_type="bool")
        self.assertEquals(settings.get(test_key), True)
        self.assertNotEqual(settings.get(test_key), False)
        Settings.objects.get(key=test_key).delete()

        # test false
        Settings.objects.create(key=test_key, value="false", value_type="bool")
        self.assertEquals(settings.get(test_key), False)
        self.assertNotEqual(settings.get(test_key), True)
        Settings.objects.get(key=test_key).delete()

    def test_integer_key(self):
        test_key = "test_integer_key"

        Settings.objects.create(key=test_key, value="666", value_type="int")
        self.assertEquals(settings.get(test_key), 666)
        self.assertNotEqual(settings.get(test_key), "666")
        Settings.objects.get(key=test_key).delete()

        Settings.objects.create(key=test_key, value="666_wrong_integer", value_type="int")
        try:
            self.assertEquals(settings.get(test_key), "666_wrong_integer")
        except ValueError:
            pass
        else:
            self.fail("Should throw ValueError exception")

    def test_float_key(self):
        test_key = "test_float_key"

        Settings.objects.create(key=test_key, value="0.666", value_type="float")
        self.assertEquals(settings.get(test_key), 0.666)
        self.assertNotEqual(settings.get(test_key), "0.666")
        Settings.objects.get(key=test_key).delete()

        Settings.objects.create(key=test_key, value="0.666_wrong_float", value_type="float")
        try:
            self.assertEquals(settings.get(test_key), "0.666_wrong_float")
        except ValueError:
            pass
        else:
            self.fail("Should throw ValueError exception")

    def test_cache(self):
        test_key = "test_cache_key"
        Settings.objects.create(key=test_key, value="test_value")
        self.assertEquals(settings.get(test_key), "test_value")
        count_queries = len(connection.queries)

        for x in range(10):
            self.assertEquals(settings.get(test_key), "test_value")

        # Count queries should not be changed
        self.assertEquals(count_queries, len(connection.queries))

    def test_cache_invalidation(self):
        test_key = "test_cache_invalidation_key"

        obj = Settings.objects.create(key=test_key, value="test_value")
        self.assertEquals(settings.get(test_key), "test_value")

        # Test invalidation on update
        obj.value = "new_test_value"
        obj.save()
        self.assertEquals(settings.get(test_key), "new_test_value")
        self.assertNotEqual(settings.get(test_key), "test_value")
        self.assertNotEqual(settings.get(test_key), None)

        # Test invalidation on delete
        obj.delete()
        self.assertEqual(settings.get(test_key), None)