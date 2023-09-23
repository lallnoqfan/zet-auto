from argparse import ArgumentParser, Namespace

from modules import SavesHandler
from controller import Controller
from modules.db import GameData, GameDataDAO


class ArgsParser:

    @classmethod
    def run(cls) -> None:

        parser = ArgumentParser()
        subparser = parser.add_subparsers(dest='command')

        read_all_parser = subparser.add_parser('all')
        read_all_parser.set_defaults(func=cls.read_all)

        create_parser = subparser.add_parser('new')
        create_parser.add_argument('name', type=str,
                                   help='New save name')
        create_parser.set_defaults(func=cls.create)

        delete_parser = subparser.add_parser('del')
        delete_parser.add_argument('name', type=str,
                                   help='Name of save to delete')
        delete_parser.set_defaults(func=cls.delete)

        update_parser = subparser.add_parser('set')
        update_parser.add_argument('name', type=str,
                                   help='Name of save to update')
        update_parser.add_argument('-t', dest='thread', type=str,
                                   help='New thread url')
        update_parser.set_defaults(func=cls.update)

        auto_parser = subparser.add_parser('run')
        auto_parser.add_argument('name', type=str,
                                 help='Name of save to run')
        auto_parser.set_defaults(func=cls.run_save)

        args = parser.parse_args()

        args.func(args)

    @staticmethod
    def read_all(args: Namespace) -> None:

        names = SavesHandler.get_list()

        if len(names) == 0:
            print("No saves found")
            return

        for name in names:
            model = SavesHandler.load(name)

            print(f"Name   - {name}")
            print(f"Board  - {model.board or 'Not set'}")
            print(f"Thread - {model.thread or 'Not set'}")

            if not model.players:
                print("No players")
                print()
                continue

            print("Players:")
            for player in model.players:
                print(f"\tName - {player.name}")
                print(f"\t\tHEX   - {player.color_hex}")
                print(f"\t\tRGB   - {player.color_rgb}")
                print(f"\t\tTiles - {len(player.tiles)}")
                print()
            print()

    @staticmethod
    def create(args: Namespace) -> None:

        name = args.name

        if SavesHandler.exists(name):
            print(f"Save '{name}' already exists")
            return

        SavesHandler.dump(args.name, GameData())

        print(f"Created new save '{name}'")

    @staticmethod
    def delete(args: Namespace) -> None:

        name = args.name

        if not SavesHandler.exists(name):
            print(f"Save '{name}' does not exist")
            return

        SavesHandler.delete(name)

        print(f"Deleted save '{name}'")

    @staticmethod
    def update(args: Namespace) -> None:

        name = args.name

        if not SavesHandler.exists(name):
            print(f"Save '{name}' does not exist")
            return

        dao = GameDataDAO(SavesHandler.load(name))

        if not args.thread:
            print("No params specified")
            return

        dao.link = args.thread  # todo: add validation
        SavesHandler.dump(name, dao.model)

        print(f"Updated save '{name}'")

    @staticmethod
    def run_save(args: Namespace) -> None:

        name = args.name

        if not SavesHandler.exists(name):
            print(f"Save '{name}' does not exist")

        Controller(name).loop()
