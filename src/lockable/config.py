import os


def get_auth_token():
    return os.environ['LOCKABLE_AUTH_TOKEN']
