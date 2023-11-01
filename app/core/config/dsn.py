from typing import Annotated

from pydantic import UrlConstraints
from pydantic_core import Url

OracleDsn = Annotated[
    Url,
    UrlConstraints(
        allowed_schemes=[
            "oracle+oracledb",
            "oracle+cx_oracle",
        ]
    ),
]
