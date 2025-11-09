from os import getenv

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env"))


def _getenv_bool(key: str, default_value: bool = False) -> bool:
    return getenv(key, str(default_value)).lower() in ("1", "true")


class ConnectionConfig:
    USE_PROXY = _getenv_bool("USE_PROXY")
    PROXY = getenv("PROXY", None) if USE_PROXY else None


class Keys:
    USERCODE = getenv('USERCODE', "")
    USERCODE_AUTH = getenv('USERCODE_AUTH', "")
    PASSCODE_AUTH = getenv('PASSCODE_AUTH', "")


class DvachConfig:
    BASE_URL = "https://2ch.su"


class AppConfig:
    MAKE_PEREKATS = _getenv_bool("MAKE_PEREKATS", False)
    READONLY = _getenv_bool("READONLY", False)
    SAVE_MAPS = _getenv_bool("SAVE_MAPS", False)
