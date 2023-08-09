from datetime import datetime
from time import sleep, perf_counter
from traceback import print_tb
from typing import List, Optional

from PIL import Image
from requests import Response
from requests.exceptions import ConnectionError
from webcolors import hex_to_rgb

from errors import ThreadNotSetException
from models import Player, RollBase, Usercode
from modules import CommentParser, PasteHandler, PremodHandler, \
    ResourcesHandler, SavesHandler
from modules.api import DvachAPIHandler, DvachThread, Post, \
    DvachPostingSchemaIn, ImageFile


class Controller:

    def __init__(self, model_name: str) -> None:

        self.comment_parser = CommentParser()
        self.res_handler = ResourcesHandler()
        self.saves_handler = SavesHandler()

        self.name = model_name
        self.model = self.saves_handler.load(model_name)

        self.paste_handler = PasteHandler()
        self.paste_handler.set_paste(self.model.paste)

        passcode_data = Usercode()

        self.api = DvachAPIHandler(
            passcode_data.usercode,
            passcode_data.usercode_auth,
            passcode_data.passcode_auth,
        )

    def set_thread(self, url: str) -> None:
        self.model.last_number = 1
        self.model.thread = url.split('/')[-1].split('.')[0]
        self.model.board = url.split('/')[-3]

    def set_thread_num(self, num: int) -> None:
        self.set_thread(f"https://2ch.hk/{self.model.board}/res/{num}.html")

    def get_map_image(self) -> Image.Image:
        return self.res_handler.draw_map(self.model.players)

    def get_players_image(self) -> Image.Image:
        return self.res_handler.draw_players(self.model.players)

    def get_player(self, name: Optional[str] = None,
                   color: Optional[str] = None) -> Player | None:

        if not name and not color:
            return

        for player in self.model.players:
            if (not name or player.name == name) and \
                    (not color or player.color_hex == color):
                return player

    def check_player(self, name: Optional[str] = None,
                     color: Optional[str] = None) -> bool:

        if not name and not color:
            return False

        for player in self.model.players:
            if player.name == name or player.color_hex == color:
                return True

        return False

    def add_player(self, name: str, color: str) -> Player | None:

        if self.check_player(name=name) or \
                self.check_player(color=color):
            return

        player = Player(
            name=name,
            color_hex=color,
            color_rgb=hex_to_rgb(color),
        )

        self.model.players.append(player)

        return player

    def del_empty_players(self) -> None:

        self.model.players = [player for player in self.model.players if player.tiles]
        self.model.roll_bases = []

    def get_roll_base(self, post_num: int) -> RollBase | None:
        return next((rb for rb in self.model.roll_bases
                     if rb.post_num == post_num), None)

    def add_roll_base(self, player: Player, post_num: int) -> RollBase | None:

        if self.get_roll_base(post_num):
            return

        roll_base = RollBase(
            player=player,
            post_num=post_num,
        )

        self.model.roll_bases.append(roll_base)

        return roll_base

    def add_tiles(self, roll_base_number: int, roll_number: int,
                  tiles: List[str], roll_value: int) -> None:

        # check if roll has value
        if not roll_value:
            return

        roll_base = self.get_roll_base(roll_base_number)

        # check if roll base exists
        if not roll_base:
            self.paste_handler.invalid_roll_base(roll_number, roll_base_number)
            return

        player = roll_base.player

        self.paste_handler.add_line()

        while roll_value and tiles:

            # check if tiles exists
            _f = False
            for tile in tiles:
                if not self.res_handler.tile_exists(tile):
                    _f = True
                    tiles.remove(tile)
                    self.paste_handler.invalid_tile(roll_number, tile)
            if _f:
                continue

            # check if player owns tiles
            _f = False
            for tile in tiles:
                if tile in player.tiles:
                    _f = True
                    tiles.remove(tile)
                    self.paste_handler.already_owns(roll_number, tile)
            if _f:
                continue

            # if player has no tiles
            if not player.tiles:
                for tile in tiles:

                    attacked = self.del_tile(tile)

                    if not attacked:
                        self.paste_handler.creation(roll_number, tile, player.name)
                    else:
                        self.paste_handler.creation_attack(
                            roll_number, tile, player.name, attacked
                        )

                    player.tiles.append(tile)
                    tiles.remove(tile)
                    roll_value -= 1

                    break
                continue

            # if player has tiles
            _f = False
            player_tiles = set(player.tiles)
            for tile in tiles:
                for route in self.res_handler.get_tile(tile).get('routes'):
                    if route not in player_tiles:
                        continue

                    _f = True

                    attacked = self.del_tile(tile)

                    if not attacked:
                        self.paste_handler.capture(roll_number, tile, player.name)
                    else:
                        self.paste_handler.capture_attack(
                            roll_number, tile, player.name, attacked
                        )

                    player.tiles.append(tile)
                    tiles.remove(tile)
                    roll_value -= 1

                    break
                if _f:
                    break
            if _f:
                continue

            # no connected tiles remaining
            for tile in tiles:
                self.paste_handler.no_routes(roll_number, tile)

            break

        if roll_value > 0:
            self.paste_handler.roll_value_surplus(roll_number, roll_value)

        self.paste_handler.add_line()

    def del_tile(self, tile_id: str) -> str | None:

        for player in self.model.players:
            if tile_id in player.tiles:
                player.tiles.remove(tile_id)
                return player.name

    def parse_roll_base(self, post: Post) -> bool:

        data = self.comment_parser.parse_roll_base(post.comment)

        if not data:
            return False

        name, color = data

        # name length check
        if len(name) > 50:  # hardcode
            self.paste_handler.too_long_name(post.num)
            return True

        player = self.get_player(name, color)

        # adding new roll base to existing player
        if player:
            self.add_roll_base(player, post.num)
            self.paste_handler.new_roll_base(post.num)
            return True

        # ignore if player with same name exists
        if self.check_player(name=name):
            self.paste_handler.same_name(post.num)
            return True

        # or with same color
        if self.check_player(color=color):
            self.paste_handler.same_color(post.num)
            return True

        # creating new player
        player = self.add_player(name, color)
        self.add_roll_base(player, post.num)
        self.paste_handler.new_player(post.num)

        return True

    def parse_roll(self, post: Post) -> bool:

        data = self.comment_parser.parse_roll(post.comment)

        if not data:
            return False

        roll_base_number, tiles = data
        value = self.comment_parser.get_roll_value(post.num)

        self.add_tiles(roll_base_number, post.num, tiles, value)

        return True

    def parse_post(self, post: Post) -> None:

        post.comment = self.comment_parser.clear(post.comment)

        if self.parse_roll_base(post):
            return
        if self.parse_roll(post):
            return
        # TODO: reply to players who did not specify tiles in the roll

    def parse_thread(self, thread: DvachThread) -> None:

        for post in thread.posts:

            if post.number > 500:  # hardcoded bump limit
                break

            if post.number <= self.model.last_number:
                continue

            self.parse_post(post)
            self.model.last_number = post.number

    def _posting(self, schema: DvachPostingSchemaIn,
                 name: str) -> Response | None:

        c, result = 5, 0
        r = None

        while not result and c:
            r = self.api.post_posting(schema)
            result = r.json().get("result")
            c -= 1
            print(r, r.json())
            if not result:
                self.sleep(5)

        if not result:
            print(f"!!! {name} failed !!!")
        else:
            print(f"{name} succeeded")

        return r

    def posting_bump(self) -> None:

        schema = DvachPostingSchemaIn(
            board=self.model.board,
            thread=self.model.thread,
            comment='Бамп',
        )

        self._posting(schema, 'Bump')

    def posting_post(self) -> None:

        map_image = self.get_map_image()
        players_image = self.get_players_image()

        schema = DvachPostingSchemaIn(
            board=self.model.board,
            thread=self.model.thread,
            comment=self.paste_handler.get_paste(),
            files=[
                ImageFile(name='map.png', image=map_image),
                ImageFile(name='players.png', image=players_image),
            ],
        )

        r = self._posting(schema, 'Post')
        if r:
            self.paste_handler.clear_paste()

    def posting_thread(self) -> None:

        self.del_empty_players()

        files = [ImageFile(name='map.png', image=self.get_map_image())]
        if self.model.players:
            files.append(ImageFile(name='players.png',
                                   image=self.get_players_image()))

        data = DvachPostingSchemaIn(
            board=self.model.board,
            comment=self.res_handler.get_op_post(),
            files=files,
        )

        r = self._posting(data, 'Thread creation')

        if not r:
            return

        self.set_thread_num(r.json().get('thread'))

        cookies, d = r.cookies, dict()
        for cookie in cookies:
            if cookie.name[:2] == 'op':
                d.update({cookie.name: cookie.value})  # noqa
        self.api.update_cookies(d)
        self.model.cookies.update(d)

    def posting_announcement(self, thread_num: str | int) -> None:

        new_thread = f"https://2ch.hk/{self.model.board}/" \
                     f"res/{self.model.thread}.html\n"

        schema = DvachPostingSchemaIn(
            board=self.model.board,
            thread=thread_num,
            comment=f"***{new_thread * 3}***",
        )

        self._posting(schema, 'Аnnouncement')

    def fetch_thread(self) -> DvachThread | None:
        return self.api.get_thread(self.model.board, self.model.thread)

    def check_drowning(self) -> bool:

        thread = self.fetch_thread()

        for post in thread.posts[::-1]:

            if post.sage:
                continue

            post_time = post.datetime.split()
            post_time = post_time[0] + ' ' + post_time[2]
            post_time = datetime.strptime(post_time, "%d/%m/%y %H:%M:%S")

            delta = datetime.now() - post_time

            return delta.seconds >= 60  # hardcoded bumps timeout

    def check_bump_limit(self) -> bool:

        if not self.model.last_number >= 500:  # hardcoded bump limit
            return False

        self.paste_handler.bump_limit()
        self.posting_post()
        self.sleep()

        old_thread = self.model.thread

        self.posting_thread()
        self.sleep()

        self.posting_announcement(old_thread)

        # TODO: отправить оповещение о перекаке в брг

        return True

    @staticmethod
    def sleep(timeout: int = 15) -> None:

        start_time = perf_counter()
        passed = perf_counter() - start_time

        while passed < timeout:
            passed = perf_counter() - start_time
            print(f"\rSleeping... {int(timeout - passed):>2}", end='')
            sleep(0.1)
        print()

    def loop_iter(self) -> None:

        if not self.model.board or not self.model.thread:
            raise ThreadNotSetException

        print(f"{f'  {datetime.now()}  ':=^80}")

        print("Fetching thread...")
        thread = self.fetch_thread()

        if not thread:
            print("Thread not found, creating new one...")
            self.posting_thread()
            return

        print("Parsing thread...")
        self.parse_thread(thread)

        if self.paste_handler.get_paste():
            print(f"{f'  paste  ':*^60}")
            print(self.paste_handler.get_paste())
            print('*' * 60)

            print("Posting map...")
            self.posting_post()
            return

        print("== No new tiles to draw ==")

        print("Checking bump limit...")
        if self.check_bump_limit():
            return

        print("Checking drowning...")
        if self.check_drowning(thread):
            self.posting_bump()
            return

    def loop(self) -> None:

        print(f"\n{'':*^50}")
        print(f"{' CTRL+C to stop loop ':*^50}")
        print(f"{'':*^50}\n")

        while True:

            try:

                self.loop_iter()

                print("Saving model...")
                self.model.paste = self.paste_handler.get_paste()
                self.saves_handler.dump(self.name, self.model)

            except ThreadNotSetException as e:
                print(e.message)

                print(f"Want to create new one? board - {self.model.board} (y/n)")
                answer = input()

                if answer != 'y':
                    break

                if not self.model.board:
                    print("Enter board code: ")
                    self.model.board = input()

                self.posting_thread()

            except ConnectionError:
                print("Connection error\n"
                      "Check your internet connection and try again")

            except Exception as e:

                print('\n' + '=' * 50)
                print(f"!!!{' UNHANDLED EXCEPTION OCCURED ': ^44}!!!")
                print(f"!!!{' KLOZET ZABILSYA ': ^44}!!!")
                print(f"!!!{' POVTORYAU KLOZET ZABILSYA ': ^44}!!!")
                print('=' * 50 + '\n')

                print(e)
                print_tb(e.__traceback__)

            finally:
                self.sleep()
