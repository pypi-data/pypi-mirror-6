__author__ = 'sathley'


class ValidationError(Exception):

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class UserAuthError(Exception):

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class AppacitiveError(Exception):
    def __init__(self, status=None):
        self.code = None
        self.message = None
        self.additional_messages = None
        self.reference_id = None
        self.version = None

        if status is not None:
            self.code = status.get('code', 0)
            self.message = status.get('message', None)
            self.additional_messages = status.get('additionalmessages', [])
            self.reference_id = status['referenceid']
            self.version = status['version']