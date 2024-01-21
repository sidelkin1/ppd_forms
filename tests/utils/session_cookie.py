import json
from base64 import b64encode
from typing import Any

from itsdangerous import TimestampSigner


def create_session_cookie(data: Any, secret_key: Any) -> str:
    signer = TimestampSigner(str(secret_key))
    return signer.sign(
        b64encode(json.dumps(data).encode("utf-8")),
    ).decode("utf-8")
