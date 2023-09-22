from typing import Dict, List, Optional

from webcolors import hex_to_rgb

from .models import GameData, Player, RollBase


class GameDataDAO:

    def __init__(self, game_data_model: GameData):
        self._model = game_data_model

    @property
    def model(self) -> GameData:
        return self._model

    @property
    def link(self) -> str:
        return (f"https://2ch.hk/{self._model.board}"
                f"/res/{self._model.thread}.html")

    @link.setter
    def link(self, new_val: str) -> None:
        self._model.thread = new_val.split('/')[-1].split('.')[0]
        self._model.board = new_val.split('/')[-3]
        self._model.last_number = 1

    @property
    def board(self) -> str:
        return self._model.board

    @board.setter
    def board(self, new_val: str) -> None:
        self._model.board = new_val

    @property
    def thread(self) -> str:
        return self._model.thread

    @thread.setter
    def thread(self, new_val: str) -> None:
        self._model.thread = new_val

    @property
    def paste(self) -> str:
        return self._model.paste

    @paste.setter
    def paste(self, new_paste: str) -> None:
        self._model.paste = new_paste

    @property
    def last_number(self) -> int:
        return self._model.last_number

    @last_number.setter
    def last_number(self, new_val: int) -> None:
        self._model.last_number = new_val

    @property
    def cookies(self) -> Dict[str, str]:
        return self._model.cookies

    @property
    def players(self) -> List[Player]:
        return self._model.players

    def get_player(
            self, *,
            name: Optional[str] = None,
            color: Optional[str] = None,
            rb_num: Optional[int] = None,
    ) -> Player | None:

        if not name and not color and rb_num is None:
            return

        if rb_num:
            player = next((
                rb.player
                for rb in self._model.roll_bases
                if (
                    (rb.post_num == rb_num) and
                    (not name or rb.player.name == name) and
                    (not color or rb.player.color_hex == color)
                )
            ), None)

            if player:
                return player

        return next((
            player
            for player in self._model.players
            if (
                (not name or player.name == name) and
                (not color or player.color_hex == color)
            )
        ), None)

    def check_player(
            self, *,
            name: Optional[str] = None,
            color: Optional[str] = None,
            rb_num: Optional[int] = None,
    ) -> bool:

        if name and next((
                True
                for player in self._model.players
                if player.name == name
        ), False):
            return True

        if color and next((
                True
                for player in self._model.players
                if player.color_hex == color
        ), False):
            return True

        if rb_num and next((
                True
                for rb in self._model.roll_bases
                if rb.post_num == rb_num
        ), False):
            return True

        return False

    def add_player(self, name: str, color: str) -> Player | None:

        if self.check_player(name=name, color=color):
            return

        player = Player(
            name=name,
            color_hex=color,
            color_rgb=hex_to_rgb(color),
        )

        self._model.players.append(player)

        return player

    def del_empty_players(self) -> None:
        self._model.players = [
            player
            for player in self._model.players
            if player.tiles
        ]

    empty_players = property(fdel=del_empty_players)

    @property
    def roll_bases(self) -> List[RollBase]:
        return self._model.roll_bases

    @roll_bases.deleter
    def roll_bases(self) -> None:
        self._model.roll_bases = []

    def get_roll_base(self, post_num: int) -> RollBase | None:
        return next((
            rb
            for rb in self._model.roll_bases
            if rb.post_num == post_num
        ), None)

    def add_roll_base(
            self, player: Player, post_num: int
    ) -> RollBase | None:

        if self.get_roll_base(post_num):
            return

        roll_base = RollBase(
            player=player,
            post_num=post_num,
        )

        self._model.roll_bases.append(roll_base)

        return roll_base

    def del_tile(self, tile_id: str) -> str | None:

        player = next((
            player
            for player in self._model.players
            if tile_id in player.tiles
        ), None)

        if player:
            player.tiles.remove(tile_id)
            return player.name

    def is_tile_free(self, tile_id: str) -> bool:
        for player in self._model.players:
            if tile_id in player.tiles:
                return False
        return True
