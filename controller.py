from datetime import datetime
from difflib import get_close_matches
from logging import basicConfig, error as log_error, ERROR
from time import sleep, perf_counter
from traceback import print_tb
from typing import List, Dict

from PIL import Image
from requests import Response
from requests.exceptions import ConnectionError

from config import ConnectionConfig, Keys
from errors import ThreadNotSetException
from modules import CommentParser, PasteHandler, PremodHandler, \
    ResourcesHandler, SavesHandler
from modules.api import DvachAPIHandler, DvachThread, Post, \
    DvachPostingSchemaIn, ImageFile
from modules.db import GameDataDAO


class Controller:

    def __init__(self, model_name: str) -> None:

        self.name = model_name
        self.dao = GameDataDAO(SavesHandler.load(model_name))

        self.premod_handler = PremodHandler()
        self.paste_handler = PasteHandler()
        self.paste_handler.paste = self.dao.paste

        self.api = DvachAPIHandler(
            usercode=Keys.USERCODE,
            usercode_auth=Keys.USERCODE_AUTH,
            passcode_auth=Keys.USERCODE_AUTH,
            use_proxy=ConnectionConfig.USE_PROXY,
            proxy=ConnectionConfig.PROXY,
        )

    def get_map_image(self) -> Image.Image:
        return ResourcesHandler.draw_map(self.dao.players)

    def get_players_image(self) -> Image.Image:
        return ResourcesHandler.draw_players(self.dao.players)

    def _pre_addition(self, roll_base_number: int, roll_number: int) -> bool:

        roll_base = self.dao.get_roll_base(roll_base_number)
        if not roll_base:
            self.paste_handler.invalid_roll_base(roll_number, roll_base_number)
            return False

        return True

    def add_tiles(self, roll_base_number: int, roll_number: int,
                  tiles: List[str], roll_value: int) -> int:

        if not self._pre_addition(roll_base_number, roll_number):
            return roll_value

        player = self.dao.get_player(rb_num=roll_base_number)

        # check if tiles exists
        for tile in tiles:
            if not ResourcesHandler.tile_exists(tile):
                tiles.remove(tile)
                self.paste_handler.invalid_tile(roll_number, tile)

        # check if player owns tiles
        for tile in tiles:
            if tile in player.tiles:
                _f = True
                tiles.remove(tile)
                self.paste_handler.already_owns(roll_number, tile)

        while roll_value > 0 and tiles:

            # if player has no tiles
            if not player.tiles:
                for tile in tiles:

                    attacked = self.dao.del_tile(tile)

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
                for route in ResourcesHandler.get_tile(tile).get('routes'):
                    if route not in player_tiles:
                        continue

                    _f = True

                    attacked = self.dao.del_tile(tile)

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

        return roll_value

    def add_tiles_neutral(self, roll_base_number: int, roll_number: int,
                          roll_value: int) -> int:

        if not self._pre_addition(roll_base_number, roll_number):
            return roll_value

        player = self.dao.get_player(rb_num=roll_base_number)
        if not player.tiles:
            self.paste_handler.expansion_without_tiles(roll_number)
            return roll_value

        free_tiles: Dict[str, float] = {}
        checked_tiles = []

        while roll_value > 0:
            # getting nearby tiles
            for tile in player.tiles:

                if tile in checked_tiles:
                    continue
                checked_tiles.append(tile)

                for routed in ResourcesHandler.get_tile(tile).get('routes'):

                    if not self.dao.is_tile_free(routed):
                        continue

                    distance = ResourcesHandler.calc_distance(tile, routed)
                    if not free_tiles.get(routed):
                        free_tiles[routed] = distance
                    else:
                        free_tiles[routed] = min(free_tiles[routed], distance)

            if not free_tiles:
                break

            # getting key with min distance to player tiles
            nearest = min(free_tiles, key=free_tiles.get)

            player.tiles.append(nearest)
            roll_value -= 1
            free_tiles.__delitem__(nearest)
            self.paste_handler.capture(roll_number, nearest, player.name)

        if roll_value > 0:
            self.paste_handler.expansion_no_free_tiles(roll_number)

        return roll_value

    def add_tiles_against(self, roll_base_number: int, roll_number: int,
                          roll_value: int, attacked_name: str) -> int:

        if not self._pre_addition(roll_base_number, roll_number):
            return roll_value

        # check if player has tiles
        attacking = self.dao.get_roll_base(roll_base_number).player
        if not attacking.tiles:
            self.paste_handler.against_without_tiles(roll_number)
            return roll_value

        # try to find the closest match in players' names
        match = get_close_matches(
            attacked_name, [player.name for player in self.dao.players], 1
        )
        if not match:
            self.paste_handler.against_no_matches(roll_number)
            return roll_value

        # check if attacked player has tiles
        attacked = self.dao.get_player(name=match[0])
        if not attacked.tiles:
            self.paste_handler.against_no_tiles(roll_number, attacked.name)
            return roll_value

        tiles: Dict[str, float] = dict()
        checked_tiles = []

        while roll_value > 0:
            for tile in attacking.tiles:

                if tile in checked_tiles:
                    continue
                checked_tiles.append(tile)

                for routed in ResourcesHandler.get_tile(tile).get('routes'):

                    if routed not in attacked.tiles:
                        continue

                    distance = ResourcesHandler.calc_distance(tile, routed)
                    if not tiles.get(routed):
                        tiles[routed] = distance
                    else:
                        tiles[routed] = min(tiles[routed], distance)

            if not tiles:
                break

            nearest = min(tiles, key=tiles.get)

            attacking.tiles.append(nearest)
            attacked.tiles.remove(nearest)
            roll_value -= 1
            tiles.__delitem__(nearest)
            self.paste_handler.capture_attack(roll_number, nearest,
                                              attacking.name, attacked.name)

        if roll_value > 0:
            self.paste_handler.against_no_routes(roll_number, attacked.name)

        return roll_value

    def parse_roll_base(self, post: Post) -> bool:

        data = CommentParser.parse_roll_base(post.comment)

        if not data:
            return False

        name, color = data

        # name length check
        if len(name) > 50:
            self.paste_handler.too_long_name(post.num)
            return True

        # non-cyrillic symbols check
        if not CommentParser.contains_cyrillic_only(name):
            self.paste_handler.non_cyrillic(post.num)
            return True

        # user moderation
        mod_answer, mod_reason = self.premod_handler.moderate(name)
        if not mod_answer:
            if mod_reason == 'in black list':
                self.paste_handler.black_listed_name(post.num)
            else:
                self.paste_handler.creation_denied(post.num, mod_reason)
            return True

        # after all checks

        # adding new roll base to existing player
        player = self.dao.get_player(name=name, color=color)
        if player:
            self.dao.add_roll_base(player, post.num)
            self.paste_handler.new_roll_base(post.num)
            return True

        # ignore if player with same name exists
        if self.dao.check_player(name=name):
            self.paste_handler.same_name(post.num)
            return True

        # or with same color
        if self.dao.check_player(color=color):
            self.paste_handler.same_color(post.num)
            return True

        # creating new player
        player = self.dao.add_player(name, color)
        self.dao.add_roll_base(player, post.num)
        self.paste_handler.new_player(post.num)

        return True

    def parse_roll(self, post: Post, roll_value: int) -> int:

        data = CommentParser.parse_roll(post.comment)

        if not data:
            return roll_value

        roll_base_number, tiles = data

        roll_value = self.add_tiles(roll_base_number, post.num, tiles, roll_value)

        return roll_value

    def parse_roll_neutral(self, post: Post, roll_value: int) -> int:

        rb_num = CommentParser.parse_roll_on_neutral(post.comment)
        if not rb_num:
            return roll_value

        roll_value = self.add_tiles_neutral(rb_num, post.num, roll_value)

        return roll_value

    def parse_roll_against(self, post: Post, roll_value: int) -> int:

        data = CommentParser.parse_roll_against(post.comment)

        if not data:
            return roll_value

        rb_num, attacked_name = data

        roll_value = self.add_tiles_against(
            rb_num, post.num, roll_value, attacked_name
        )

        return roll_value

    def parse_post(self, post: Post) -> None:

        post.comment = CommentParser.clear(post.comment)

        if self.parse_roll_base(post):
            return

        roll_value = CommentParser.get_roll_value(post.num)
        if roll_value <= 0:
            return

        self.paste_handler.add_line()

        roll_value = self.parse_roll(post, roll_value)
        if roll_value <= 0:
            self.paste_handler.add_line()
            return

        roll_value = self.parse_roll_neutral(post, roll_value)
        if roll_value <= 0:
            self.paste_handler.add_line()
            return

        roll_value = self.parse_roll_against(post, roll_value)

        if roll_value <= 0:
            self.paste_handler.add_line()
            return

        self.paste_handler.roll_value_surplus(post.num, roll_value)
        self.paste_handler.add_line()

    def parse_thread(self, thread: DvachThread) -> None:

        for post in thread.posts:

            if post.number <= self.dao.last_number:
                continue

            if post.number > 500:  # hardcoded bump limit
                break

            self.parse_post(post)
            self.dao.last_number = post.number

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
            print(f"!!! {name} - провалено !!!")
        else:
            print(f"{name} - ок")

        return r

    def posting_bump(self) -> None:

        schema = DvachPostingSchemaIn(
            board=self.dao.board,
            thread=self.dao.thread,
            comment='Бамп',
        )

        self._posting(schema, 'Бамп')

    def posting_post(self) -> None:

        map_image = self.get_map_image()
        players_image = self.get_players_image()

        schema = DvachPostingSchemaIn(
            board=self.dao.board,
            thread=self.dao.thread,
            comment=self.paste_handler.paste,
            files=[
                ImageFile(name='map.png', image=map_image),
                ImageFile(name='players.png', image=players_image),
            ],
        )

        r = self._posting(schema, 'Постинг')
        if r:
            del self.paste_handler.paste

    def posting_thread(self) -> None:

        del self.dao.empty_players
        del self.dao.roll_bases

        files = [ImageFile(name='map.png', image=self.get_map_image())]
        if self.dao.players:
            files.append(ImageFile(name='players.png',
                                   image=self.get_players_image()))

        data = DvachPostingSchemaIn(
            board=self.dao.board,
            comment=ResourcesHandler.get_op_post(),
            files=files,
        )

        r = self._posting(data, 'Создание треда')

        if not r:
            return

        self.dao.thread = r.json().get('thread')

        cookies, d = r.cookies, dict()
        for cookie in cookies:
            if cookie.name[:2] == 'op':
                d.update({cookie.name: cookie.value})  # noqa
        self.api.update_cookies(d)
        self.dao.cookies.update(d)

    def posting_announcement(self, thread_num: str | int) -> None:

        new_thread_link = self.dao.link

        schema = DvachPostingSchemaIn(
            board=self.dao.board,
            thread=thread_num,
            comment=f"***{new_thread_link * 3}***",
        )

        self._posting(schema, 'Анонс переката')

    def fetch_thread(self) -> DvachThread | None:
        return self.api.get_thread(self.dao.board, self.dao.thread)

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

        if not self.dao.last_number >= 500:  # hardcoded bump limit
            return False

        self.paste_handler.bump_limit()
        self.posting_post()
        self.sleep()

        if not AppConfig.MAKE_PEREKATS:
            print("отмена переката - конфиг сказал ноу")
            return True

        old_thread = self.dao.thread

        self.posting_thread()
        self.sleep()

        self.posting_announcement(old_thread)

        # TODO: отправить оповещение о перекаке в брг # fr?

        return True

    @staticmethod
    def sleep(timeout: int = 15) -> None:

        start_time = perf_counter()
        passed = perf_counter() - start_time

        while passed < timeout:
            passed = perf_counter() - start_time
            print(f"\rСпим... {int(timeout - passed):>2}", end='')
            sleep(0.1)
        print()

    def loop_iter(self) -> None:

        if not self.dao.board or not self.dao.thread:
            raise ThreadNotSetException

        print(f"{f'  {datetime.now()}  ':=^80}")

        print("Получаем тред...")
        thread = self.fetch_thread()

        if not thread:
            print("Тред не найдем, создаём новый...")
            self.posting_thread()
            return

        print("Парсим тред...")
        self.parse_thread(thread)

        if self.paste_handler.paste:
            print(f"{f'  паста  ':*^60}")
            print(self.paste_handler.paste)
            print('*' * 60)

            print("Постим карту...")
            self.posting_post()
            return

        print("== Нет новых захватов для отрисовки ==")

        print("Проверяем бамплимит...")
        if self.check_bump_limit():
            return

        print("Проверяем на затопленность...")
        if self.check_drowning():
            self.posting_bump()
            return

    def loop(self) -> None:

        print(f"\n{'':*^50}")
        print(f"{' CTRL+C для выхода из лупа ':*^50}")
        print(f"{'':*^50}\n")

        basicConfig(level=ERROR,
                    filename=str(__file__).replace(
                        'controller.py', 'errors.log'
                    ),
                    filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

        f = True
        while True:

            try:

                self.loop_iter()

                print("Сохраняем модель...")
                self.dao.paste = self.paste_handler.paste
                SavesHandler.dump(self.name, self.dao.model)

            except ThreadNotSetException as e:
                print(e.message)

                print(f"Хотите запилить новый? Доска - {self.dao.board} (да/нет)")
                answer = input().lower()

                if answer not in {"да", "y"}:
                    break

                if not self.dao.board:
                    print("Введите код доски: ")
                    self.dao.board = input()

                self.posting_thread()

            except ConnectionError:
                print("Ошибка соеднинения\n"
                      "Проверьте своё интернет соединение и попробуйте позже")

            except KeyboardInterrupt:
                print("\nОстановлено клавиатурой")
                f = False

            except Exception as e:

                print('\n' + '=' * 50)
                print(f"!!!{' ПРОИЗОШЛА ЧУДОВИЩНАЯ ОШИБКА ': ^44}!!!")
                print(f"!!!{' КЛОЗЕТ ЗАБИЛСЯ ': ^44}!!!")
                print(f"!!!{' ПОВТОРЯЮ КЛОЗЕТ ЗАБИЛСЯ ': ^44}!!!")
                print('=' * 50 + '\n')

                print(e)
                print_tb(e.__traceback__)
                print()
                log_error(e, exc_info=True)

            finally:
                if not f:
                    return
                self.sleep()
