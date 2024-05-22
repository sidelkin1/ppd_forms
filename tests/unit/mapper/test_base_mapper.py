from functools import _lru_cache_wrapper

from app.infrastructure.db.types.unify import BaseMapper, SplitMode


def test_split_words_extract(base_mapper: BaseMapper):
    input_str = "word1, word2; word3\nword4\rword5"
    expected = [
        ("word1", 0),
        ("word2", 0),
        ("word3", 0),
        ("word4", 0),
        ("word5", 0),
    ]
    assert base_mapper.split_words(input_str) == expected


def test_split_words_split_in(base_mapper: BaseMapper):
    base_mapper.split_mode = SplitMode.split_in
    input_str = "word1, word2; word3\nword4\rword5"
    expected = [
        ("word1", 0),
        ("word2", 0),
        ("word3", 0),
        ("word4", 0),
        ("word5", 0),
    ]
    assert base_mapper.split_words(input_str) == expected


def test_unique_words(base_mapper: BaseMapper):
    input_list = [("word1", 0), ("word2", 0), ("word1", 0)]
    expected = [("word1", 0), ("word2", 0)]
    assert base_mapper.unique_words(input_list) == expected


def test_sort_words(base_mapper: BaseMapper):
    input_list = [("word2", 2), ("word1", 1), ("word3", 3)]
    expected = [("word1", 1), ("word2", 2), ("word3", 3)]
    assert base_mapper.sort_words(input_list, 3) == expected


def test_join_words(base_mapper: BaseMapper):
    input_list = [("word1", 0), ("word2", 0), ("word3", 0)]
    expected = "word1,word2,word3"
    assert base_mapper.join_words(input_list) == expected


def test_getitem(base_mapper: BaseMapper):
    input_str = "word1, word2; word3\nword4\rword5"
    expected = "word1,word2,word3,word4,word5"
    assert base_mapper[input_str] == expected


def test_getitem_with_cache(base_mapper: BaseMapper):
    input_str = "word1, word2; word3\nword4\rword5"
    assert isinstance(base_mapper._getitem, _lru_cache_wrapper)
    base_mapper[input_str]
    initial_cache_info = base_mapper._getitem.cache_info()
    assert initial_cache_info.misses == 1
    base_mapper[input_str]
    second_cache_info = base_mapper._getitem.cache_info()
    assert second_cache_info.hits == 1
    assert second_cache_info.misses == 1
