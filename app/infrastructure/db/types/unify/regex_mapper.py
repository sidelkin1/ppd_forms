import re

from app.infrastructure.db.types.unify.base_mapper import WordOrder
from app.infrastructure.db.types.unify.simple_mapper import (
    ReplaceDict,
    SimpleMapper,
)


class RegexMapper(SimpleMapper):
    def __init__(
        self,
        *,
        pattern: re.Pattern | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.pattern = pattern

    def replace_word(
        self, word: WordOrder, max_order: int
    ) -> tuple[WordOrder, int]:
        if self.pattern is not None:
            if match := self.pattern.match(word[self.WORD]):
                if match.lastgroup is not None:
                    word = self.replace[match.lastgroup]
        return word, max(max_order, word[self.ORDER])

    def update(
        self,
        replace: ReplaceDict | None = None,
        pattern: re.Pattern | None = None,
    ) -> None:
        if replace is not None:
            self.replace.update(replace)
        if pattern is not None:
            self.pattern = pattern
