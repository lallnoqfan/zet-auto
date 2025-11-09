from typing import Optional


class PasteHandler:
    def __init__(self) -> None:
        self._paste = ''

    @property
    def paste(self) -> str:
        s = self._paste
        if not s:
            return ''
        while s[-1] == '\n':
            s = s[:-1]
        return s

    @paste.setter
    def paste(self, new_paste: str) -> None:
        self._paste = new_paste

    @paste.deleter
    def paste(self) -> None:
        self._paste = ""

    def _add_reply(self, num: int, message: str) -> None:
        self._paste += f">>{num} {message}\n"

    def add_line(self) -> None:
        if not self._paste:
            return
        if self._paste[-2:] != "\n\n":
            self._paste += "\n"

    def bump_limit(self):
        self._paste += "**" + "СССССТТТТТОООООПППППРРРРРОООООЛЛЛЛЛЛЛЛЛЛ\n" * 5 + "**"

    def new_player(self, num: int) -> None:
        self._add_reply(num, "%%страна добавлена%%")

    def new_roll_base(self, num: int) -> None:
        self._add_reply(num, "%%роллбаза добавлена%%")

    def creation(self, num: int, tile: str, player_name: str) -> None:
        self._add_reply(num, f"**\"{player_name}\" создаётся на {tile.upper()}**")

    def creation_attack(self, num: int, tile: str, player_name: str, attacked_name: str) -> None:
        self._add_reply(num, f"**\"{player_name}\" создаётся на "
                             f"{tile.upper()}, захватывая клетку \"{attacked_name}\"**")

    def capture(self, num: int, tile: str, player_name: str) -> None:
        self._add_reply(num, f"\"{player_name}\" захватывает нейтральную {tile.upper()}")

    def capture_attack(self, num: int, tile: str, player_name: str, attacked_name: str) -> None:
        self._add_reply(num, f"**\"{player_name}\" захватывает {tile.upper()} у \"{attacked_name}\"**")

    def same_name(self, num: int) -> None:
        self._add_reply(num, "%%имя занято%%")

    def same_color(self, num: int) -> None:
        self._add_reply(num, "%%цвет занят%%")

    def too_long_name(self, num: int) -> None:
        self._add_reply(num, "%%макс. длина названия - 50 символов%%")  # hardcode

    def non_cyrillic(self, num: int) -> None:
        self._add_reply(num, "%%имя может содержать только кириллицу и пробелы%%")

    def creation_denied(self, num: int, reason: Optional[str]):
        self._add_reply(num, f"%%создание запрещено{f', причина: {reason}' if reason else ''}%%")

    def black_listed_name(self, num: int) -> None:
        self.creation_denied(num, "имя в черном списке")

    def invalid_roll_base(self, num: int, roll_base_num: int) -> None:
        self._add_reply(num, f"%%пост >>{roll_base_num} не является роллбазой%%")

    def already_owns(self, num: int, tile: str) -> None:
        self._add_reply(num, f"%%{tile.upper()} уже под вашим контролем%%")

    def roll_value_surplus(self, num: int, val: int) -> None:
        end = "а" if val == 1 else "ов"
        self._add_reply(num, f"%%излишек из {val} захват{end} не был распределён и сгорает%%")

    def no_routes(self, num: int, tile: str) -> None:
        self._add_reply(num, f"%%нет доступных путей к {tile.upper()}%%")

    def invalid_tile(self, num: int, tile: str) -> None:
        self._add_reply(num, f"%%территория {tile.upper()} не существует%%")

    def expansion_without_tiles(self, num: int) -> None:
        self._add_reply(num, "%%нельзя роллить на расширение, если у страны нет территорий%%")

    def expansion_no_free_tiles(self, num: int) -> None:
        self._add_reply(num, "%%нет доступных для расширения нейтральных территорий%%")

    def against_without_tiles(self, num: int) -> None:
        self._add_reply(num, "%%нельзя роллить на атаку, если у страны нет территорий%%")

    def against_no_tiles(self, num: int, name: str) -> None:
        self._add_reply(num, f"%%{name} не имеет территорий%%")

    def against_no_routes(self, num: int, name: str) -> None:
        self._add_reply(num, f"%%нет доступных путей к \"{name}\"%%")

    def against_no_matches(self, num: int) -> None:
        self._add_reply(num, f"%%не найдено близких совпадений с указанным именем%%")
