from pprint import pprint

from o2lib.classes.logged_in_user import SingletonLoggedInUser


__all__ = [
    'logged_user',
]


def logged_user():
    return SingletonLoggedInUser().user
