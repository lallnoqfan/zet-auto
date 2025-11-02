class ThreadNotSetException(Exception):

    def __init__(self, message=''):
        self.message = 'Тред не выбран'
        if message:
            self.message += ': ' + message
        super().__init__(self.message)
