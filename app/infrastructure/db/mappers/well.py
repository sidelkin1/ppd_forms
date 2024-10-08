import re
from enum import Enum

from app.infrastructure.db.mappers.base import BaseMapper, WordOrder


class TRANSLATE_TO(Enum):
    RUS = 1
    ENG = 2


class WellMapper(BaseMapper):
    branch_pattern: re.Pattern = re.compile(r"(?<=\w)[BВ]\d")
    zero_pattern: re.Pattern = re.compile(r"^0+")

    def __init__(
        self,
        *,
        del_orzid: bool = False,
        del_branch: bool = False,
        del_zero: bool = False,
        translate_to: TRANSLATE_TO = TRANSLATE_TO.ENG,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.del_branch = del_branch
        self.del_zero = del_zero

        rus_tab = "АВГКНПРУЧ"
        eng_tab = "ABGKNPRUX"
        if translate_to is TRANSLATE_TO.ENG:
            in_tab, out_tab = rus_tab, eng_tab
        elif translate_to is TRANSLATE_TO.RUS:
            in_tab, out_tab = eng_tab, rus_tab
        else:
            raise TypeError(
                f"Unsupported type {type(translate_to)}"
                " of `translate_to` (expected type is"
                f" {type(TRANSLATE_TO.ENG)})"
            )

        if del_orzid:
            self.tran_tab = str.maketrans(in_tab, out_tab, "НN")
        else:
            self.tran_tab = str.maketrans(  # type: ignore[assignment]
                in_tab, out_tab
            )

    def replace_word(
        self, word: WordOrder, max_order: int
    ) -> tuple[WordOrder, int]:
        new_value = word[self.WORD].upper().translate(self.tran_tab)
        if self.del_branch:
            new_value = self.branch_pattern.sub("", new_value)
        if self.del_zero:
            new_value = self.zero_pattern.sub("", new_value)
        return (new_value, word[self.ORDER]), max(max_order, word[self.ORDER])
