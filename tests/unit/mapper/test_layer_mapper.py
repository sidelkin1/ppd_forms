from app.infrastructure.db.types.unify import LayerMapper
from app.infrastructure.db.types.unify.layer_mapper import flatten


def test_flatten():
    nested_iterable = [1, (2, 3), [4, 5], 6, [(7, 8), 9]]
    expected_flat_list = [1, (2, 3), 4, 5, 6, (7, 8), 9]
    assert list(flatten(nested_iterable)) == expected_flat_list


def test_replace_word(layer_mapper: LayerMapper):
    word_order = ("A", 0)
    expected_word, expected_order = [("a", 1)], 1
    replaced_word, max_order = layer_mapper.replace_word(word_order, 0)
    assert replaced_word == expected_word
    assert max_order == expected_order


def test_unique_words(layer_mapper: LayerMapper):
    result = [("alpha", 1), [("alpha", 1), ("beta", 2)]]
    expected_unique = [("alpha", 1), ("beta", 2)]
    unique_words = layer_mapper.unique_words(result)
    assert unique_words == expected_unique


def test_sort_words(layer_mapper: LayerMapper):
    result = [[("beta", 2), ("alpha", 1)], ("gamma", 3)]
    expected_sorted = [("alpha", 1), ("beta", 2), ("gamma", 3)]
    sorted_words = layer_mapper.sort_words(result, 2)
    assert sorted_words == expected_sorted


def test_update(layer_mapper: LayerMapper):
    assert layer_mapper.replace == {"A": [("a", 1)], "B": [("b", 2)]}
    layer_mapper.update(
        {"B": ("b", 10), "A+B": ("A,B", 0), "A+D": ("A,d", 0), "C": ("c", 3)}
    )
    assert layer_mapper.replace == {
        "A": [("a", 1)],
        "A+B": [("a", 1), ("b", 10)],
        "A+D": [("a", 1), ("d", 0)],
        "B": [("b", 10)],
        "C": [("c", 3)],
    }
