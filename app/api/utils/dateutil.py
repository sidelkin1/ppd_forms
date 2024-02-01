from datetime import tzinfo

from dateutil import tz


def get_tz(location: str) -> tzinfo:
    result = tz.gettz(location)
    assert result is not None
    return result


tz_utc = get_tz("UTC")
