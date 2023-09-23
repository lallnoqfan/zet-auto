from os import system

from InquirerPy.base import Choice
from InquirerPy.inquirer import select
from InquirerPy.prompts import ListPrompt


class InquirerApp:

    @classmethod
    def run(cls):
        cls.clean_screen()
        cls._wip_dummy().execute()

    @staticmethod
    def _wip_dummy() -> ListPrompt:
        return select(
            message='WIP',
            choices=[
                Choice(value=None, name='Назад'),
            ]
        )

    @staticmethod
    def clean_screen():
        system("cls||clear")
