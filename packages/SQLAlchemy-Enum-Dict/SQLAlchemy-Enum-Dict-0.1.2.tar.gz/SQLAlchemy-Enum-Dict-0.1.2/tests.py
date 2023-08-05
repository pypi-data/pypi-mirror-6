import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from unittest import TestCase
from sqlalchemy_enum_dict import EnumDict


def get_all_types(exclude=()):
    all_types = dict(int=[-1, 0, 1, 1L],
                     float=[1.0],
                     str=['str'],
                     bool=[True, False],
                     none=[None],
                     list=[list()],
                     tuple=[tuple()],
                     dict=[dict()],
                     set=[set()],
                     object=[object()])

    if exclude:
        for excl in exclude:
            if excl in all_types:
                del all_types[excl]

    result = []
    for types in all_types.values():
        result.extend(types)
    return result


class TestEnumDict(TestCase):
    def setUp(self):
        self.reserved_key_names = ('_key', '_value_dict', '_values')
        self.values = (
            ('key_1', {
                'db': 1,
                'title': 'title 1',
                'url': 'http://google.com',
            }),
            ('key_2', {
                'db': 2,
                'title': 'title 2',
                'url': 'http://yandex.ru',
            }),
            ('key_3', {
                'db': 3,
                'title': 'title 3',
                'url': 'http://wikipedia.org',
            }),
        )
        self.enums = EnumDict(*self.values)

    def tearDown(self):
        self.reserved_key_names = None
        self.values = None
        self.enums = None

    def test_known_values(self):
        for key, value_dict in self.values:
            enum = getattr(self.enums, key)
            self.assertEqual(value_dict['db'], enum.db)
            self.assertEqual(value_dict['title'], enum.title)
            self.assertEqual(value_dict['url'], enum.url)

    def test_get_key(self):
        for key, value_dict in self.values:
            enum = getattr(self.enums, key)
            self.assertEqual(key, enum.get_key())

    def test_get_by_db_value_existent(self):
        for key, value_dict in self.values:
            enum = getattr(self.enums, key)
            db_value = value_dict['db']
            found_enum_by_int = self.enums.get_by_db_value(db_value)
            found_enum_by_str = self.enums.get_by_db_value(str(db_value))
            self.assertEqual(enum, found_enum_by_int)
            self.assertEqual(enum, found_enum_by_str)

    def test_get_by_db_value_not_existent(self):
        not_existent_values = [10 ** 5, 8 ** 5, 9 ** 5]
        for db_value in not_existent_values:
            result = self.enums.get_by_db_value(db_value)
            self.assertEqual(result, None)

    def test_enums_len(self):
        self.assertEqual(len(self.values), len(self.enums))

    def test_enums_items_len(self):
        for key, value_dict in self.values:
            enum = getattr(self.enums, key)
            self.assertEqual(len(value_dict), len(enum))

    def test_equality_for_enums_items(self):
        same_enum = EnumDict(*self.values)
        self.assertEqual(self.enums.key_1, same_enum.key_1)

    def test_bad_enums_keys_types(self):
        for bad_type in get_all_types(exclude=['str']):
            value = (bad_type, {'db': 0})
            self.assertRaises(TypeError, EnumDict, value)

    def test_bad_enums_values_keys_types(self):
        for bad_type in get_all_types(exclude=('str', 'list', 'set', 'dict')):
            value = ('key', {'db': 1, bad_type: 0})
            self.assertRaises(TypeError, EnumDict, value)

    def test_bad_enums_values_values_types(self):
        for bad_type in get_all_types(exclude=['dict']):
            value = ('key', bad_type)
            self.assertRaises(ValueError, EnumDict, value)

    def test_bad_reserved_enums_keys_names(self):
        for bad_name in self.reserved_key_names:
            value = (bad_name, {'db': 1})
            self.assertRaises(ValueError, EnumDict, value)

    def test_bad_reserved_enums_values_keys_names(self):
        for bad_name in self.reserved_key_names:
            value = ('key', {bad_name: 1})
            self.assertRaises(ValueError, EnumDict, value)

    def test_bad_enums_values_absence_db_key(self):
        for bad_db_key in ['a', 'b', 'c']:
            value = ('key', {bad_db_key: 1})
            self.assertRaises(ValueError, EnumDict, value)

    def test_value_int_calling(self):
        for value in self.enums:
            self.assertEqual(value.db, int(value))


if __name__ == '__main__':
    unittest.main()
