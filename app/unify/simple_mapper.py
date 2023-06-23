from typing import Optional

from app.unify.base_mapper import BaseMapper, WordOrder

ReplaceDict = dict[str, WordOrder]


class SimpleMapper(BaseMapper):

    def __init__(
        self,
        *,
        replace: Optional[ReplaceDict] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.replace = replace or {}

    def replace_word(
        self,
        word: WordOrder,
        max_order: int
    ) -> tuple[WordOrder, int]:
        word = self.replace.get(word[self.WORD], word)
        return word, max(max_order, word[self.ORDER])

    def update(
        self,
        replace: Optional[ReplaceDict] = None,
    ) -> None:
        self.replace.update(replace)
