from pathlib import Path
from pickle import dump, load
from typing import List

from models import GameData


class SavesHandler:

    _extension: str = '.zet'
    _path: Path = Path(__file__).parent / 'saves'

    _path.mkdir(exist_ok=True)

    @classmethod
    def _get_path(cls, name: str) -> Path:
        return cls._path / f"{name}{cls._extension}"

    @classmethod
    def get_list(cls) -> List[str]:
        return [
            p.stem
            for p in cls._path.iterdir()
            if p.suffix == cls._extension
        ]

    @classmethod
    def exists(cls, name: str) -> bool:
        return cls._get_path(name).exists()

    @classmethod
    def load(cls, name: str) -> GameData:
        with cls._get_path(name).open('rb') as f:
            return load(f)

    @classmethod
    def dump(cls, name: str, model: GameData) -> None:
        with cls._get_path(name).open('wb') as f:
            dump(model, f)

    @classmethod
    def delete(cls, name: str) -> None:
        cls._get_path(name).unlink(missing_ok=True)
