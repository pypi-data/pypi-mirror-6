from sqlalchemy.types import SmallInteger
from sqlalchemy.types import TypeDecorator
from .extensions import EnumDict


class EnumDictForInt(TypeDecorator):
    impl = SmallInteger
    Enum = EnumDict

    def __init__(self, values, *args, **kwargs):
        self.values = values
        TypeDecorator.__init__(self, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        if hasattr(value, 'db'):
            return value.db
        elif (bool(isinstance(value, (int, long))
              and not isinstance(value, bool))):
            return value
        return None

    def process_result_value(self, value, dialect):
        return self.values.get_by_db_value(value)
