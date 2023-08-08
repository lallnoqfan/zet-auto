class ThreadNotSetException(Exception):

    def __init__(self, message=''):
        self.message = 'Thread not set'
        if message:
            self.message += ': ' + message
        super().__init__(self.message)
