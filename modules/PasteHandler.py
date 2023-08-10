from typing import Optional


class PasteHandler:

    def __init__(self) -> None:
        self.paste = ''

    def get_paste(self) -> str:
        s = self.paste
        if not s:
            return s
        while s[-1] == '\n':
            s = s[:-1]
        return s

    def set_paste(self, s: str) -> None:
        self.paste = s

    def clear_paste(self) -> None:
        self.paste = ''

    def _add_reply(self, num: int, message: str) -> None:
        self.paste += f">>{num} {message}\n"

    def add_line(self) -> None:
        if not self.paste:
            return
        if self.paste[-2:] != '\n\n':
            self.paste += '\n'

    def bump_limit(self):
        self.set_paste(self.paste + "**" + "СССССТТТТТОООООППППП  "
                                           "РРРРРОООООЛЛЛЛЛЛЛЛЛЛ\n" * 5 + "**")

    def new_player(self, num: int) -> None:
        self._add_reply(num, '%%страна добавлена%%')

    def new_roll_base(self, num: int) -> None:
        self._add_reply(num, '%%роллбаза добавлена%%')

    def creation(self, num: int, tile: str, player_name: str) -> None:
        self._add_reply(num, f"**\"{player_name}\" "
                             f"создаётся на {tile.upper()}**")

    def creation_attack(self, num: int, tile: str,
                        player_name: str, attacked_name: str) -> None:
        self._add_reply(num, f"**\"{player_name}\" создаётся на "
                             f"{tile.upper()}, захватывая клетку \"{attacked_name}\"**")

    def capture(self, num: int, tile: str, player_name: str) -> None:
        self._add_reply(num, f"\"{player_name}\" захватывает "
                             f"нейтральную {tile.upper()}")

    def capture_attack(self, num: int, tile: str,
                       player_name: str, attacked_name: str) -> None:
        self._add_reply(num, f"**\"{player_name}\" захватывает "
                             f"{tile.upper()} у \"{attacked_name}\"**")

    def same_name(self, num: int) -> None:
        self._add_reply(num, '%%имя занято%%')

    def same_color(self, num: int) -> None:
        self._add_reply(num, '%%цвет занят%%')

    def too_long_name(self, num: int) -> None:
        self._add_reply(num, '%%макс. длина названия - '
                             '50 символов%%')  # hardcode

    def non_cyrillic(self, num: int) -> None:
        self._add_reply(num, '%%имя может содержать только '
                             'кириллицу и пробелы%%')

    def creation_denied(self, num: int, reason: Optional[str]):
        self._add_reply(num, f"%%создание запрещено"
                             f"{f', причина: {reason}' if reason else ''}%%")

    def black_listed_name(self, num: int) -> None:
        self.creation_denied(num, "имя в черном списке")

    def invalid_roll_base(self, num: int, roll_base_num: int) -> None:
        self._add_reply(num, f'%%пост >>{roll_base_num} '
                             f'не является роллбазой%%')

    def already_owns(self, num: int, tile: str) -> None:
        self._add_reply(num, f"%%{tile.upper()} уже под вашим контролем%%")

    def roll_value_surplus(self, num: int, val: int) -> None:
        end = 'а' if val == 1 else 'ов'
        self._add_reply(num, f"%%излишек из {val} захват{end} "
                             f"не был распределён и сгорает%%")

    def no_routes(self, num: int, tile: str) -> None:
        self._add_reply(num, f'%%нет доступных путей к {tile.upper()}%%')

    def invalid_tile(self, num: int, tile: str) -> None:
        self._add_reply(num, f'%%клетка {tile.upper()} не существует%%')

    def expansion_without_tiles(self, num: int) -> None:
        self._add_reply(num, '%%нельзя роллить на расширение, '
                             'если у вас нет клеток%%')

    def expansion_no_free_tiles(self, num: int) -> None:
        self._add_reply(num, '%%нет доступных для расширения клеток%%')

    def against_without_tiles(self, num: int) -> None:
        self._add_reply(num, '%%нельзя роллить на атаку, '
                             'если у вас нет клеток%%')

    def against_no_routes(self, num: int, name: str) -> None:
        self._add_reply(num, f'%%нет доступных путей к \"{name}\"%%')

    def against_no_matches(self, num: int) -> None:
        self._add_reply(num, f'%%не найдено близких '
                             f'совпадений с указанным именем%%')
