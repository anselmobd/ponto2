from pprint import pprint

from o2lib.classes.logged_in_user import SingletonLoggedInUser

from django.contrib.auth.models import User


__all__ = [
    'logged_user',
]


def logged_user():
    return SingletonLoggedInUser().user


def first_user():
    return User.objects.first()


def first_user_id():
    return first_user().id
