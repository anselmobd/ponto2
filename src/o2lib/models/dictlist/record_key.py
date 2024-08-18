from pprint import pprint

from django.db.models.base import ModelState


__all__ = [
    'record_keys',
    'record_keys2dict',
    'record2dict',
]


def record_keys(record):
    return [
        key
        # for key in record.__dict__
        for key in record
        if not isinstance(record[key], ModelState)
    ]


def record_keys2dict(record, keys, fkey=lambda x: x):
    return {
        # fkey(key): record.__dict__[key]
        fkey(key): record[key]
        for key in keys
    }


def record2dict(record, fkey=lambda x: x):
    return record_keys2dict(
        record,
        record_keys(record),
        fkey
    )
