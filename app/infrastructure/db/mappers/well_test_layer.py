import re

from app.infrastructure.db.mappers.base import BaseMapper, WordOrder


class WellTestLayerMapper(BaseMapper):
    layer_pattern: re.Pattern = re.compile(
        r"[\w+\-()]+\s+(?P<layer>[\w+\-()`]+)"
    )

    def replace_word(
        self, word: WordOrder, max_order: int
    ) -> tuple[WordOrder, int]:
        new_value = word[self.WORD]
        if match := self.layer_pattern.match(new_value):
            new_value = match.group("layer")
        else:
            new_value = ""
        return (new_value, word[self.ORDER]), max(max_order, word[self.ORDER])
