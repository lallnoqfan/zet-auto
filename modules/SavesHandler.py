from os import mkdir, remove
from os.path import exists
from pickle import dump, load

from models import GameData


class SavesHandler:

    def __init__(self) -> None:

        self.extension = '.zet'
        self.path = str(__file__).replace(
            str(__file__).split('\\')[-1], 'saves\\'
        )

        if not exists(self.path):
            mkdir(self.path)

    def exists(self, name: str) -> bool:
        return exists(f"{self.path}{name}{self.extension}")

    def load(self, name: str) -> GameData:
        return load(open(f"{self.path}{name}{self.extension}", "rb"))

    def dump(self, name: str, model: GameData) -> None:
        dump(model, open(f"{self.path}{name}{self.extension}", "wb"))

    def delete(self, name: str) -> None:
        if exists(f"{self.path}{name}{self.extension}"):
            remove(f"{self.path}{name}{self.extension}")
