class ThreadNotSetException(Exception):

    def __init__(self, message=''):
        self.message = "Тред не выбран"
        if message:
            self.message += f": {message}"
        super().__init__(self.message)


class ThreadNotFoundException(Exception):
    def __init__(self, message=''):
        self.message = "Тред не найден"
        if message:
            self.message += f": {message}"
        super().__init__(self.message)
