from json import load
from typing import List, Dict

from PIL import Image, ImageDraw, ImageFont
from webcolors import hex_to_rgb

from models import Player


class ResourcesHandler:

    def __init__(self) -> None:

        self.path = str(__file__).replace(
            str(__file__).split('\\')[-1], 'resources\\'
        )

        self.map: Image.Image = Image.open(f"{self.path}map.png").convert('RGB')
        self.tiles_data: Dict = load(open(f"{self.path}tiles_data.json",
                                          encoding='utf-8'))

    def get_op_post(self) -> str:
        with open(f"{self.path}op_post.txt", encoding='utf-8') as f:
            return f.read()

    def get_tile(self, tile_id: str) -> Dict | None:
        return self.tiles_data.get(tile_id)

    def tile_exists(self, tile_id: str) -> bool:
        return tile_id in self.tiles_data

    def calc_distance(self, first_tile_id: str,  second_tile_id: str) -> float:

        first_tile = self.get_tile(first_tile_id)
        second_tile = self.get_tile(second_tile_id)

        x1, y1 = first_tile.get('x'), first_tile.get('y')
        x2, y2 = second_tile.get('x'), second_tile.get('y')

        distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        return distance

    def draw_map(self, players: List[Player]) -> Image.Image:

        map_image = self.map.copy()

        for player in players:
            for tile in player.tiles:

                tile = self.get_tile(tile)

                ImageDraw.floodfill(
                    map_image,
                    (tile.get('x'), tile.get('y')),
                    player.color_rgb,
                )

        return map_image

    def _draw_player_title(self, name: str, color: str) -> Image.Image:
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
                f"{self.path}CodenameCoderFree4F-Bold.ttf", 40,
                encoding='unic'),
        )

        return img

    def draw_players(self, players: List[Player]) -> Image.Image:

        players = [player for player in players if player.tiles]
        players = {player.color_hex: player.name for player in players}
        # players = {key: players[key] for key in sorted(players)}

        w, h = 960, 50 * len(players)
        img = Image.new('RGB', (w, h), (255, 255, 255))

        i = 0
        for key in players:
            title_img = self._draw_player_title(players[key], key)
            img.paste(title_img, (0, i))
            i += 50

        return img
