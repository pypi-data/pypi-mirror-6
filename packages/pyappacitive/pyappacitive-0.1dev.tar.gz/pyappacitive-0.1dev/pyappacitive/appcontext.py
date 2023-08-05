__author__ = 'sathley'


class ApplicationContext(object):
    def __init__(self):
        pass

    __logged_in_user = None

    __user_token = None

    @staticmethod
    def get_logged_in_user():
        return ApplicationContext.__logged_in_user

    @staticmethod
    def get_user_token():
        return ApplicationContext.__user_token

    @staticmethod
    def set_logged_in_user(user):
        ApplicationContext.__logged_in_user = user

    @staticmethod
    def set_user_token(token):
        ApplicationContext.__user_token = token


