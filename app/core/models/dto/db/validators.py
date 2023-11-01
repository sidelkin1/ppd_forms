from typing import Annotated, Any, TypeVar

import pandas as pd
from pydantic.functional_validators import BeforeValidator

T = TypeVar("T")


def empty_str_to_none(v: Any) -> Any:
    return None if v == "" else v


def nan_to_none(v: Any) -> Any:
    return None if pd.isna(v) else v


EmptyStrToNone = Annotated[T | None, BeforeValidator(empty_str_to_none)]
NanToNone = Annotated[T | None, BeforeValidator(nan_to_none)]
EmptyStrOrNanToNone = Annotated[
    T | None,
    BeforeValidator(empty_str_to_none),
    BeforeValidator(nan_to_none),
]
