from typing import Any

from app.infrastructure.db.types.unify.base_mapper import BaseMapper, WordOrder

ReplaceDict = dict[str, Any]  # FIXME need more precise type conversion


class SimpleMapper(BaseMapper):
    def __init__(
        self,
        *,
        replace: ReplaceDict | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.replace = replace or {}

    def replace_word(
        self, word: WordOrder, max_order: int
    ) -> tuple[WordOrder, int]:
        word = self.replace.get(word[self.WORD], word)
        return word, max(max_order, word[self.ORDER])

    def update(
        self,
        replace: ReplaceDict | None = None,
    ) -> None:
        if replace is not None:
            self.replace.update(replace)
