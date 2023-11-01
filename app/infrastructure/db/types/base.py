import sqlalchemy.types as types


class BaseType(types.TypeDecorator):
    __abstract__ = True

    impl = types.String

    cache_ok = True

    # TODO Данный метод реализован для того, чтобы в подклассах
    # атрибут `cache_ok` появлялся в `self.__class__.__dict__`
    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.cache_ok = BaseType.cache_ok

    def process_bind_param(self, value, dialect):
        return self.mapper[value]

    @property
    def python_type(self):
        return str
