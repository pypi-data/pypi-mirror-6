from django.db import connection
from django.test import TestCase
from django.test.utils import override_settings

from .import settings


class SimpleSettingsTestCase(TestCase):
    def test_get_set(self):
        test_key = "test_get_key"
        test_value = "test_get_value"

        settings.set(test_key, test_value)
        self.assertEquals(settings.get(test_key), test_value)
        self.assertEquals(settings[test_key], test_value)

    def test_set_override(self):
        test_key = "test_set_override_key"

        settings.set(test_key, "test_value_1")
        settings.set(test_key, "test_value_2")
        self.assertEquals(settings.get(test_key), "test_value_2")

    def test_get_unknown_key(self):
        test_key = "test_get_unknown_settings_key"

        self.assertEquals(settings.get(test_key), None)
        try:
            self.assertEquals(settings[test_key], "test_get_unknown_settings")
        except KeyError:
            pass
        else:
            self.fail("Should throw KeyError exception")

    def test_delete(self):
        test_key = "test_delete_key"
        test_value = "test_delete_value"

        settings.set(test_key, test_value)
        settings.delete(test_key)
        self.assertNotEqual(settings.get(test_key), test_value)

        # test delete unexisted setting
        try:
            settings.delete(test_key)
        except KeyError:
            pass
        else:
            self.fail("Should throw KeyError exception")

    def test_boolean_key(self):
        test_key = "test_boolean_key"

        # test true
        settings.set(test_key, True)
        self.assertEquals(settings.get(test_key), True)
        self.assertNotEqual(settings.get(test_key), False)

        # test false
        settings.set(test_key, False)
        self.assertEquals(settings.get(test_key), False)
        self.assertNotEqual(settings.get(test_key), True)

    def test_integer_key(self):
        test_key = "test_integer_key"

        settings.set(test_key, 666)
        self.assertEquals(settings.get(test_key), 666)
        self.assertNotEqual(settings.get(test_key), "666")

    def test_float_key(self):
        test_key = "test_float_key"

        settings.set(test_key, 0.666)
        self.assertEquals(settings.get(test_key), 0.666)
        self.assertNotEqual(settings.get(test_key), "0.666")

    @override_settings(DEBUG=True)
    def test_cache(self):
        test_key = "test_cache_key"
        test_value = "test_cache_vaue"

        settings.set(test_key, test_value)
        self.assertEquals(settings.get(test_key), test_value)
        count_queries = len(connection.queries)

        for x in range(10):
            self.assertEquals(settings.get(test_key), test_value)

        # Count queries should not be changed
        self.assertEquals(count_queries, len(connection.queries))

    def test_cache_invalidation(self):
        test_key = "test_cache_invalidation_key"
        test_value = "test_cache_invalidation_value"

        settings.set(test_key, test_value)
        self.assertEquals(settings.get(test_key), test_value)

        # Test invalidation on update
        settings.set(test_key, "new_test_value")
        self.assertEquals(settings.get(test_key), "new_test_value")
        self.assertNotEqual(settings.get(test_key), test_value)
        self.assertNotEqual(settings.get(test_key), None)

        # Test invalidation on delete
        settings.delete(test_key)
        self.assertEqual(settings.get(test_key), None)
