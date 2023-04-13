from pydantic.validators import str_validator


class EmptyStrToNone(str):
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v == '':
            return None
        raise ValueError('empty string allowed only')
