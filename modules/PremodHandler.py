from argparse import ArgumentParser, Namespace
from os.path import exists
from re import compile, search, IGNORECASE
from typing import List, Tuple


class PremodHandler:

    def __init__(self) -> None:

        self.path = str(__file__).replace(
            str(__file__).split('\\')[-1], 'resources\\'
        )
        self.white_list = self.get_white_list()
        self.black_list = self.get_black_list()

    @staticmethod
    def _load_file(path: str) -> List[str]:

        if exists(path):
            with open(path, "r", encoding="utf-8") as f:
                white_list = f.read().splitlines()
            return white_list

        with open(path, "w"):
            pass

        return []

    @staticmethod
    def _dump_file(lines: List[str], path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + '\n')

    def get_white_list(self) -> List[str]:
        fp = f"{self.path}white_list.txt"
        return self._load_file(fp)

    def get_black_list(self) -> List[str]:
        fp = f"{self.path}black_list.txt"
        return self._load_file(fp)

    def dump_white_list(self) -> None:
        fp = f"{self.path}white_list.txt"
        self._dump_file(self.white_list, fp)

    def dump_black_list(self) -> None:
        fp = f"{self.path}black_list.txt"
        self._dump_file(self.black_list, fp)

    def add_to_white_list(self, name: str) -> None:
        if name in self.white_list:
            return
        self.white_list.append(name)
        self.dump_white_list()

    def add_to_black_list(self, name: str) -> None:
        if name in self.black_list:
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

    def add_player(self, name: str, args: Namespace) -> Tuple[bool, None]:
        self.add_to_white_list(f"^{name}$")
        return True, None

    def ban_player(self, name: str, args: Namespace) -> Tuple[bool, str | None]:
        self.add_to_black_list(f"^{name}$")
        reason = None
        if args.reason:
            reason = ''.join(r + ' ' for r in args.reason)[:-1]
        return False, reason

    def repeat_name(self, name: str) -> None:
        self.add_to_white_list(f"^{name}$")

    def get_parser(self) -> ArgumentParser:

        parser = ArgumentParser()
        subparser = parser.add_subparsers(dest='command')

        add_parser = subparser.add_parser('add', help='add player')
        add_parser.set_defaults(func=self.add_player)

        ban_parser = subparser.add_parser('ban', help='ban player')
        ban_parser.add_argument('-r', '--reason', type=str,
                                action='extend', nargs='+', default=[],
                                help='ban reason', dest='reason')

        repeat_parser = subparser.add_parser('name', help='repeat name')
        repeat_parser.set_defaults(func=self.repeat_name)

        ban_parser.set_defaults(func=self.ban_player)

        return parser

    def moderate(self, name) -> Tuple[bool, str | None]:
        if self.in_black_list(name):
            return False, 'in black list'
        if self.in_white_list(name):
            return True, None

        judgment: bool | None = None
        reason: str = ''

        parser = self.get_parser()

        print('=' * 70)
        print(f"!!! {'[ALERT] New player creation request (-h for help)': ^62} !!!")
        print(f"!!! {f'Name: {name}': ^62} !!!")
        print('=' * 70)

        while judgment is None:

            try:
                args = input('>>> ')
                args = parser.parse_args(args.split())

                if not args.command:
                    parser.print_help()
                    continue

                if args.func == self.repeat_name:
                    self.repeat_name(name)
                    continue

                judgment, reason = args.func(name, args)

            except SystemExit:
                if not judgment:
                    continue

        print('-' * 20, reason)
        return judgment, reason
