def _check_key(key):
    if not isinstance(key, basestring):
        raise TypeError('`key` must be str, %s found' % type(key).__name__)
    if key in ('_key', '_values', '_value_dict'):
        raise ValueError('`%s` name is reserved' % key)



class EnumDictItem(object):
    def __init__(self, key, value_dict):
        if not (isinstance(value_dict, dict) and 'db' in value_dict):
            raise ValueError('`value_dict` must be dict '
                             'with at least one key `db')

        self._key = key
        self._value_dict = value_dict
        for key, value in self._value_dict.items():
            _check_key(key)
            setattr(self, key, value)

    def __repr__(self):
        return '%s(db=%d)' % (self.get_key(), self.db)

    def __eq__(self, other):
        for key, value in self._value_dict.items():
            if not (hasattr(other, key) and getattr(other, key) == value):
                return False
        return True

    def __int__(self):
        return self.db

    def __len__(self):
        return len(self._value_dict)

    def get_key(self):
        return self._key


class EnumDict(object):
    def __init__(self, *values):
        self._values = []
        for key, value in values:
            _check_key(key)
            setattr(self, key, EnumDictItem(key, value))
            self._values.append(getattr(self, key))

    def __repr__(self):
        return 'EnumDict([%s])' % ', '.join([
            '%s{db: %d}' % (enum.get_key(), enum.db)
            for enum in self
        ])

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def get_by_db_value(self, db_value):
        if isinstance(db_value, basestring) and db_value.isdigit():
            db_value = int(db_value)
        for value in self._values:
            if value.db == db_value:
                return value
        return None
