import re

from app.infrastructure.db.types.unify import RegexMapper


def test_simple_pattern_replacement(regex_mapper: RegexMapper):
    word_order = [("123", 1), ("abc", 1), ("123abc", 1)]
    expected_result = [("NUMBER", 1), ("WORD", 1), ("NUMBER", 1)]
    for word, expected in zip(word_order, expected_result):
        replaced_word, max_order = regex_mapper.replace_word(word, 0)
        assert replaced_word == expected
        assert max_order == 1


def test_no_pattern_no_replacement(regex_mapper_no_pattern: RegexMapper):
    word_order = ("123", 1)
    expected_result = ("123", 1)
    replaced_word, max_order = regex_mapper_no_pattern.replace_word(
        word_order, 0
    )
    assert replaced_word == expected_result
    assert max_order == 1


def test_update_pattern_and_replacement(regex_mapper: RegexMapper):
    new_pattern = re.compile(r"(?P<alpha>\w+)")
    new_replace = {"alpha": ("LETTERS", 1)}
    regex_mapper.update(pattern=new_pattern, replace=new_replace)
    word_order = ("abc", 1)
    expected_result = ("LETTERS", 1)
    replaced_word, max_order = regex_mapper.replace_word(word_order, 0)
    assert replaced_word == expected_result
    assert max_order == 1
