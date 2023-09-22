from os import getenv
from typing import Any

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel


class Usercode(BaseModel):
    usercode:      str = ''
    usercode_auth: str = ''
    passcode_auth: str = ''

    def __init__(self, **data: Any):
        super().__init__(**data)

        load_dotenv(find_dotenv())
        self.usercode = getenv('USERCODE')
        self.usercode_auth = getenv('USERCODE_AUTH')
        self.passcode_auth = getenv('PASSCODE_AUTH')
