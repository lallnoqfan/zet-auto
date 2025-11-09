from argparse import ArgumentParser, Namespace

from modules import SavesHandler
from controller import Controller
from modules.db import GameData, GameDataDAO


class App:

    def __init__(self) -> None:

        parser = ArgumentParser()
        subparser = parser.add_subparsers(dest='command')

        read_all_parser = subparser.add_parser('all')
        read_all_parser.set_defaults(func=self.read_all)

        create_parser = subparser.add_parser('new')
        create_parser.add_argument('name', type=str,
                                   help='New save name')
        create_parser.set_defaults(func=self.create)

        delete_parser = subparser.add_parser('del')
        delete_parser.add_argument('name', type=str,
                                   help='Name of save to delete')
        delete_parser.set_defaults(func=self.delete)

        update_parser = subparser.add_parser('set')
        update_parser.add_argument('name', type=str, help='Name of save to update')
        update_parser.add_argument('-b', dest='board', type=str, help='New board code')
        update_parser.add_argument('-t', dest='thread', type=str, help='New thread number')
        update_parser.add_argument('-l', dest='last_number', type=str, help='New last number')
        update_parser.set_defaults(func=self.update)

        auto_parser = subparser.add_parser('run')
        auto_parser.add_argument('name', type=str,
                                 help='Name of save to run')
        auto_parser.set_defaults(func=self.run)

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        args.func(args)

    @staticmethod
    def read_all(_: Namespace) -> None:

        names = SavesHandler.get_list()

        if len(names) == 0:
            print("No saves found")
            return

        print("=" * 60)
        for name in names:
            print(f"Name: {name}")
            print(GameDataDAO.load(name))
            print("=" * 60)

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

        state_changed = False

        if args.board:
            dao.board = args.board
            state_changed = True

        if args.thread:
            dao.thread = args.thread
            state_changed = True

        if args.last_number:
            dao.last_number = int(args.last_number)
            state_changed = True

        if not state_changed:
            print("No params specified")
            return

        SavesHandler.dump(name, dao.model)

        print(f"Updated save '{name}'")

    @staticmethod
    def run(args: Namespace) -> None:

        name = args.name

        if not SavesHandler.exists(name):
            print(f"Save '{name}' does not exist")

        Controller(name).loop()


if __name__ == '__main__':
    try:
        App()
    except KeyboardInterrupt:
        print("\nStopped by keyboard")
