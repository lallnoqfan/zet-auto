from os import PathLike
from pathlib import Path
from re import compile, search, IGNORECASE
from typing import List, Tuple

from InquirerPy.base import Choice
from InquirerPy.inquirer import select, text
from InquirerPy.prompts import ListPrompt, InputPrompt
from InquirerPy.separator import Separator


class PremodHandler:

    _path: Path = Path(__file__).parent / 'resources'

    _white_list_path: Path = _path / 'white_list.txt'
    _black_list_path: Path = _path / 'black_list.txt'
    _ban_reasons_path: Path = _path / 'ban_reasons.txt'

    def __init__(self) -> None:
        self.white_list = self.get_white_list()
        self.black_list = self.get_black_list()

    @staticmethod
    def _load_file(path: str | PathLike[str]) -> List[str]:

        if not isinstance(path, PathLike):
            path = Path(path)

        if path.exists():
            with path.open('r', encoding='utf-8') as f:
                white_list = f.read().splitlines()
            return white_list

        with path.open('w'):  # creating empty file
            pass

        return []

    @staticmethod
    def _dump_file(lines: List[str], path: str | PathLike[str]) -> None:

        if not isinstance(path, PathLike):
            path = Path(path)

        with path.open('w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')

    @classmethod
    def get_white_list(cls) -> List[str]:
        return cls._load_file(cls._white_list_path)

    @classmethod
    def get_black_list(cls) -> List[str]:
        return cls._load_file(cls._black_list_path)

    @classmethod
    def get_ban_reasons(cls) -> List[str]:
        return cls._load_file(cls._ban_reasons_path)

    def dump_white_list(self) -> None:
        self._dump_file(self.white_list, self._white_list_path)

    def dump_black_list(self) -> None:
        self._dump_file(self.black_list, self._black_list_path)

    def add_to_white_list(self, name: str) -> None:
        if name in self.white_list or name in self.black_list:
            return
        self.white_list.append(name)
        self.dump_white_list()

    def add_to_black_list(self, name: str) -> None:
        if name in self.white_list or name in self.black_list:
            return
        self.black_list.append(name)
        self.dump_black_list()

    @staticmethod
    def _in_list(_list: List[str], name: str) -> bool:
        for pattern in _list:
            if search(compile(pattern, flags=IGNORECASE), name):
                return True
        return False

    def in_white_list(self, name: str) -> bool:
        return self._in_list(self.white_list, name)

    def in_black_list(self, name: str) -> bool:
        return self._in_list(self.black_list, name)

    @staticmethod
    def _select_action(player_name: str) -> ListPrompt:
        return select(
            message=f'Запрос на создание игрока\n  Название: {player_name}',
            choices=[
                Choice(value='add', name='Добавить'),
                Choice(value='ignore', name='Игнорировать'),
                Choice(value='ban', name='Забанить'),
            ],
            default='add',
        )

    @classmethod
    def _select_reason(cls, player_name: str, is_ban: bool = False) -> ListPrompt:
        reasons = cls.get_ban_reasons()
        return select(
            message=f'Причина {"бана" if is_ban else "игнора"} "{player_name}":',
            choices=[
                *[
                    Choice(value=i, name=reasons[i])
                    for i in range(len(reasons))
                ],
                Separator(),
                Choice(value=cls._input_reason, name='Указать другую...'),
                Choice(value=None, name='Без указания причины'),
            ],
            default=0,
        )

    @staticmethod
    def _input_reason(player_name: str, is_ban: bool = False) -> InputPrompt:
        return text(
            message=f'Причина {"бана" if is_ban else "игнора"} "{player_name}":'
        )

    def moderate(self, player_name: str) -> Tuple[bool, str | None]:

        # checking lists

        if self.in_black_list(player_name):
            return False, 'in black list'
        if self.in_white_list(player_name):
            return True, None

        # user judgement

        print()
        match self._select_action(player_name).execute():

            case 'add':
                self.add_to_white_list(player_name)
                return True, None

            case 'ban':
                print()
                reason = self._select_reason(player_name).execute()

                if reason == self._input_reason:
                    print()
                    reason = self._input_reason(player_name).execute()

                self.add_to_black_list(player_name)
                return False, reason
            
            case 'ignore':
                print()
                reason = self._select_reason(player_name).execute()

                if reason == self._input_reason:
                    print()
                    reason = self._input_reason(player_name).execute()

                return False, reason
