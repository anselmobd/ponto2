from pprint import pprint


__all__ = [
    'dict_def_options',
    'dict_options',
]


def dict_def_options(dictionary, default, *args):
    """
    Return dictionary[arg] for first arg in args that exists in dictionary.
    Otherwise, return default value.
    """
    for arg in args:
        try:
            return dictionary[arg]
        except KeyError:
            pass
    return default


def dict_options(dictionary, *args):
    """
    Call dict_def_options with default value None
    """
    return dict_def_options(dictionary, None, *args)
