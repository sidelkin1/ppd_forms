from app.infrastructure.db.types.unify.base_mapper import WordOrder
from app.infrastructure.db.types.unify.simple_mapper import (
    ReplaceDict,
    SimpleMapper,
)


def flatten(iterable):
    for value in iterable:
        if isinstance(value, tuple):
            yield value
            continue
        try:
            yield from value
        except TypeError:
            yield value


class LayerMapper(SimpleMapper):
    def __init__(
        self,
        *,
        replace: ReplaceDict | None = None,
        **kwargs,
    ) -> None:
        if replace:
            self.prepare_replace(replace)
            self.remake_replace(replace)
        super().__init__(replace=replace, **kwargs)

    def prepare_replace(self, replace: ReplaceDict):
        for key, value in replace.items():
            replace[key] = self.split_words(
                value[self.WORD],
                value[self.ORDER],
            )

    def remake_replace(self, replace: ReplaceDict):
        for key, pairs in replace.items():
            replace[key] = list(
                flatten(
                    self.replace.get(pair[self.WORD], pair) for pair in pairs
                )
            )

    def replace_word(
        self, word: WordOrder, max_order: int
    ) -> tuple[WordOrder, int]:
        word = self.replace.get(word[self.WORD], [word])
        max_pair_order = max(
            pair[self.ORDER] for pair in word  # type: ignore[index]
        )
        return word, max(max_order, max_pair_order)

    def unique_words(self, result: list[WordOrder]) -> list[WordOrder]:
        return super().unique_words(flatten(result))

    def sort_words(
        self, result: list[WordOrder], max_order: int
    ) -> list[WordOrder]:
        return super().sort_words(flatten(result), max_order)

    def update(
        self,
        replace: ReplaceDict | None = None,
    ) -> None:
        if replace:
            self.prepare_replace(replace)
            self.replace.update(replace)
            self.remake_replace(self.replace)
