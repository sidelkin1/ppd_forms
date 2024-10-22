from app.infrastructure.db.mappers import SimpleMapper


def test_replace_word_in_dictionary(simple_mapper: SimpleMapper):
    replaced_word, max_order = simple_mapper.replace_word(("hello", 1), 0)
    assert replaced_word == ("hi", 2)
    assert max_order == 2


def test_replace_word_not_in_dictionary(simple_mapper: SimpleMapper):
    replaced_word, max_order = simple_mapper.replace_word(("world", 1), 3)
    assert replaced_word == ("world", 1)
    assert max_order == 3


def test_update_add_new_word(simple_mapper: SimpleMapper):
    simple_mapper.update({"goodbye": ("bye", 2)})
    assert "goodbye" in simple_mapper.replace
    assert simple_mapper.replace["goodbye"] == ("bye", 2)


def test_update_existing_word(simple_mapper: SimpleMapper):
    simple_mapper.update({"hello": ("greetings", 3)})
    assert simple_mapper.replace["hello"] == ("greetings", 3)
