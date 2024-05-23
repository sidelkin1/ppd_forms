from app.infrastructure.db.types.unify import WellMapper


def test_translation_to_english(well_mapper_default: WellMapper):
    word_order = ("АВГКНПРУЧ", 1)
    expected_translation = ("ABGKNPRUX", 1)
    replaced_word, max_order = well_mapper_default.replace_word(word_order, 0)
    assert replaced_word == expected_translation
    assert max_order == 1


def test_translation_to_russian(well_mapper_translate_to_rus: WellMapper):
    word_order = ("ABGKNPRUX", 1)
    expected_translation = ("АВГКНПРУЧ", 1)
    replaced_word, max_order = well_mapper_translate_to_rus.replace_word(
        word_order, 0
    )
    assert replaced_word == expected_translation
    assert max_order == 1


def test_deletion_of_branch_code(well_mapper_del_branch: WellMapper):
    word_order = ("WELLB1", 1)
    expected_result = ("WELL", 1)
    replaced_word, max_order = well_mapper_del_branch.replace_word(
        word_order, 0
    )
    assert replaced_word == expected_result
    assert max_order == 1


def test_deletion_of_leading_zeros(well_mapper_del_zero: WellMapper):
    word_order = ("000123", 1)
    expected_result = ("123", 1)
    replaced_word, max_order = well_mapper_del_zero.replace_word(word_order, 0)
    assert replaced_word == expected_result
    assert max_order == 1


def test_deletion_of_orzid(well_mapper_del_orzid: WellMapper):
    word_order = ("Н123N", 1)
    expected_result = ("123", 1)
    replaced_word, max_order = well_mapper_del_orzid.replace_word(
        word_order, 0
    )
    assert replaced_word == expected_result
    assert max_order == 1
