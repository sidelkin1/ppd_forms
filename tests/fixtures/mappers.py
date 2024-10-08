import re

import pytest

from app.infrastructure.db.mappers import (
    TRANSLATE_TO,
    BaseMapper,
    LayerMapper,
    RegexMapper,
    SimpleMapper,
    WellMapper,
)


class BaseMapperMock(BaseMapper):
    def replace_word(self, word, max_order):
        return (word, max_order)


@pytest.fixture
def base_mapper() -> BaseMapper:
    return BaseMapperMock()


@pytest.fixture
def simple_mapper() -> SimpleMapper:
    return SimpleMapper(replace={"hello": ("hi", 2)})


@pytest.fixture
def layer_mapper() -> LayerMapper:
    return LayerMapper(replace={"A": ("a", 1), "B": ("b", 2)})


@pytest.fixture
def regex_mapper() -> RegexMapper:
    pattern = re.compile(r"(?P<word>[a-zA-Z]+)|(?P<digit>\d+)")
    return RegexMapper(
        pattern=pattern, replace={"digit": ("NUMBER", 1), "word": ("WORD", 1)}
    )


@pytest.fixture
def regex_mapper_no_pattern() -> RegexMapper:
    return RegexMapper()


@pytest.fixture
def well_mapper_default() -> WellMapper:
    return WellMapper()


@pytest.fixture
def well_mapper_translate_to_rus() -> WellMapper:
    return WellMapper(translate_to=TRANSLATE_TO.RUS)


@pytest.fixture
def well_mapper_del_branch() -> WellMapper:
    return WellMapper(del_branch=True)


@pytest.fixture
def well_mapper_del_zero() -> WellMapper:
    return WellMapper(del_zero=True)


@pytest.fixture
def well_mapper_del_orzid() -> WellMapper:
    return WellMapper(del_orzid=True)
