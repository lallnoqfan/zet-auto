from os import getenv
from typing import List, Tuple, Any

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel

# todo: rework as pandas models one day


class Player(BaseModel):
    name:      str
    color_hex: str
    color_rgb: Tuple[int, int, int]
    tiles:     List[str] = []


class RollBase(BaseModel):
    player:   Player
    post_num: int


class GameData(BaseModel):
    board:       str = 'b'
    thread:      str = ''
    last_number: int = 1
    paste:       str = ''
    players:     List[Player] = []
    roll_bases:  List[RollBase] = []


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
