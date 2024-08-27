import hashlib
import time
from pprint import pprint

from o2lib.functions import request_user


__all__ = [
    'hash_trail',
    'request_hash_trail',
]


def hash_trail(*values):
    """Devolve um hash de uma lista de valores"""
    values_to_hash = ';'.join(map(format, values))
    hash_object = hashlib.md5(values_to_hash.encode())
    return hash_object.hexdigest()


def request_hash_trail(request, *values):
    """Devolve um hash de
    - hoje
    - request user e session_key
    - uma lista de valores"""
    values = list(values)
    values.extend([
        time.strftime('%y%m%d'),
        request_user(request),
        request.session.session_key,
    ])
    return hash_trail(*values)
