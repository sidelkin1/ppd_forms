import logging
import secrets

from ldap3 import ALL, Connection, Server
from ldap3.core.exceptions import LDAPExceptionError
from pydantic import AnyUrl

logger = logging.getLogger(__name__)


def default_verify(
    default_username: str | None,
    default_password: str | None,
    username: str,
    password: str,
):
    if not default_username or not default_password:
        return False
    is_correct_username = secrets.compare_digest(
        username.encode("utf8"), default_username.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        password.encode("utf8"), default_password.encode("utf8")
    )
    return is_correct_username and is_correct_password


def ldap_verify(url: AnyUrl, username: str, password: str) -> bool:
    conn = None
    try:
        server = Server(str(url), get_info=ALL)
        conn = Connection(
            server,
            user=f"{username}@{url.host}",
            password=password,
            auto_bind=True,
        )
        conn.bind()
        if conn.result["result"] == 0:
            return True
    except LDAPExceptionError as error:
        logger.error("Not authenticated", exc_info=error)
    finally:
        if conn is not None:
            conn.unbind()
    return False
