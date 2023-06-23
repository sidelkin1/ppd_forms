import re
from abc import ABC, abstractmethod

from app.core.config import settings

WordOrder = tuple[str, int]


class BaseMapper(ABC):

    NULL_ORDER: int = 0

    WORD: int = 0
    ORDER: int = 1

    word_pattern: re.Pattern = re.compile(r'[\w+\-()`]+')

    def __init__(
        self,
        *,
        split: bool = True,
        sort: bool = False,
        unique: bool = False,
        delimiter: str = settings.delimiter,
    ) -> None:
        self.split = split
        self.sort = sort
        self.unique = unique
        self.delimiter = delimiter

    def __getitem__(self, input: str) -> str:
        result = (
            self.split_words(input) if self.split
            else [(input, self.NULL_ORDER)]
        )
        max_order = self.NULL_ORDER
        for idx, word in enumerate(result):
            result[idx], max_order = self.replace_word(word, max_order)
        if self.split and self.unique:
            result = self.unique_words(result)
        if self.split and self.sort:
            result = self.sort_words(result, max_order)
        return self.join_words(result)

    def split_words(
        self,
        input: str,
        order: int = NULL_ORDER,
    ) -> list[WordOrder]:
        return [
            (word, order)
            for word in self.word_pattern.findall(input)
        ]

    @abstractmethod
    def replace_word(
        self,
        word: WordOrder,
        max_order: int
    ) -> tuple[WordOrder, int]:
        raise NotImplementedError

    def unique_words(self, result: list[WordOrder]) -> list[WordOrder]:
        seen = set()
        return [
            word for word in result
            if word not in seen and not seen.add(word)
        ]

    def sort_words(
        self,
        result: list[WordOrder],
        max_order: int
    ) -> list[WordOrder]:
        return sorted(
            result,
            key=lambda pair: (
                pair[self.ORDER] or max_order + 1,
                pair[self.WORD],
            ),
        )

    def join_words(self, result: list[WordOrder]) -> str:
        return self.delimiter.join(pair[self.WORD] for pair in result)
