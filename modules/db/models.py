from typing import List, Tuple, Dict

from pydantic import BaseModel


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

    cookies: Dict[str, str] = dict()
