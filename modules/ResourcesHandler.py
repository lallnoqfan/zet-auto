from json import load
from pathlib import Path
from typing import List, Dict
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from webcolors import hex_to_rgb

from modules.db import Player


class ResourcesHandler:

    _path: Path = Path(__file__).parent / 'resources'
    _map: Image.Image = Image.open(_path / 'map.png').convert('RGB')

    with (_path / 'tiles_data.json').open('r', encoding='utf-8') as f:
        _tiles_data: Dict = load(f)

    @classmethod
    def get_op_post(cls) -> str:
        return (cls._path / 'op_post.txt').open('r', encoding='utf-8').read()

    @classmethod
    def get_tile(cls, tile_id: str) -> Dict | None:
        return cls._tiles_data.get(tile_id)

    @classmethod
    def tile_exists(cls, tile_id: str) -> bool:
        return tile_id in cls._tiles_data

    @classmethod
    def calc_distance(cls, first_tile_id: str,  second_tile_id: str) -> float:

        first_tile = cls.get_tile(first_tile_id)
        second_tile = cls.get_tile(second_tile_id)

        x1, y1 = first_tile.get('x'), first_tile.get('y')
        x2, y2 = second_tile.get('x'), second_tile.get('y')

        distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        return distance

    @classmethod
    def draw_map(cls, players: List[Player]) -> Image.Image:

        map_image = cls._map.copy()

        for player in players:
            for tile in player.tiles:

                tile = cls.get_tile(tile)

                ImageDraw.floodfill(
                    map_image,
                    (tile.get('x'), tile.get('y')),
                    player.color_rgb,
                )

        return map_image

    @classmethod
    def _draw_player_title(cls, name: str, color: str) -> Image.Image:
        w, h = 960, 50
        img = Image.new('RGB', (w, h), (255, 255, 255))

        ImageDraw.Draw(img).rectangle(
            xy=((5, 5), (45, 45)),
            fill=hex_to_rgb(color),
            outline=(0, 0, 0),
            width=5,
        )

        ImageDraw.Draw(img).text(
            xy=(55, 0),
            text=name,
            fill=(0, 0, 0),
            font=ImageFont.truetype(
                str(cls._path / 'CodenameCoderFree4F-Bold.ttf'),
                40,
                encoding='unic'
            ),
        )

        return img

    @classmethod
    def draw_players(cls, players: List[Player]) -> Image.Image:

        players = {
            player.color_hex: player.name
            for player in players
            if player.tiles
        }

        w, h = 960, max(50 * len(players), 10)
        img = Image.new('RGB', (w, h), (255, 255, 255))

        i = 0
        for key in players:
            title_img = cls._draw_player_title(players[key], key)
            img.paste(title_img, (0, i))
            i += 50

        return img

    @classmethod
    def save_image(cls, image: Image.Image, name: str | None = None) -> None:
        path = cls._path.parent / "saved images"
        path.mkdir(parents=True, exist_ok=True)

        if not name:
            name = f"{uuid4()}"
        image.save(path / f"{name}.png")
