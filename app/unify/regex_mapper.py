import re
from typing import Optional

from app.unify.base_mapper import WordOrder
from app.unify.simple_mapper import ReplaceDict, SimpleMapper


class RegexMapper(SimpleMapper):

    def __init__(
        self,
        *,
        pattern: Optional[re.Pattern] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.pattern = pattern

    def replace_word(
        self,
        word: WordOrder,
        max_order: int
    ) -> tuple[WordOrder, int]:
        if match := self.pattern.match(word[self.WORD]):
            word = self.replace[match.lastgroup]
        return word, max(max_order, word[self.ORDER])

    def update(
        self,
        replace: Optional[ReplaceDict] = None,
        pattern: Optional[re.Pattern] = None,
    ) -> None:
        self.replace.update(replace)
        if pattern is not None:
            self.pattern = pattern
