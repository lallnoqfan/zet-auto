from os import getenv

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env"))


def _getenv_bool(key: str, default_value: bool = False) -> bool:
    return getenv(key, str(default_value)).lower() in ("1", "true")


class ConnectionConfig:
    USE_PROXY = _getenv_bool("USE_PROXY")
    PROXY = getenv("PROXY", None) if USE_PROXY else None
