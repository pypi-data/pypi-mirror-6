# -*- coding: utf-8 -*-
"""
Module hapis.settings
=====================
Contains helper functions useful for processing settings. These should be used
during :term:`Pyramid` application configuration e.g. in an :term:`includeme`
function.
"""

from pyramid.compat import string_types
from pyramid.settings import aslist


def _dotted_or_string(config, s):
    try:
        return config.maybe_dotted(s)
    except ImportError:
        return s


def _make_kv_pair(s):
    k, v = s.split('=', 1)
    return k.strip(), v.strip()


def parse_keyvalue_pairs(config, setting, dotted=True):
    """
    If `setting` is a string, split it on newlines, then split each line on the
    first occurence of `'='` symbol and strip both parts of whitespace. Then
    create a dictionary out of those pairs. If `setting` is not a string leave
    it unchanged.

    If the optional argument `dotted` is `True`, also try to resolve each value
    in the resulting dictionary as a :term:`dotted Python name`. If it is not a
    string, leave it without attempting to do any name resolution. If it is a
    relative dotted name, consider it relative to the `package` argument
    supplied to `config`’s constructor.

    `config` should be a :term:`configurator` for the current pyramid
    application.
    """
    if isinstance(setting, string_types):
        setting = dict((
            _make_kv_pair(f) for f in aslist(setting, flatten=False)
        ))
    if dotted:
        for key, value in setting.items():
            setting[key] = _dotted_or_string(config, value)
    return setting


def parse_multiline(config, lines, dotted=True):
    """
    If `lines` is a string, split it on newlines, else leave it unchanged.

    If the optional argument `dotted` is `True`, also try to resolve each value
    in the resulting dictionary as a :term:`dotted Python name`. If it is not a
    string, leave it without attempting to do any name resolution. If it is a
    relative dotted name, consider it relative to the `package` argument
    supplied to `config`’s constructor.

    `config` should be a :term:`configurator` for the current pyramid
    application.
    """
    if isinstance(lines, string_types):
        lines = aslist(lines, flatten=False)
    if dotted:
        lines = [_dotted_or_string(config, line) for line in lines]
    return lines


def filter_by_prefix(adict, prefix):
    """
    Returns a new dictionary based on `adict` with keys that start with
    `prefix`. Also removes that prefix from keys.

    .. warning:: The function assumes that all keys in `adict` are strings.
    """
    prefix_length = len(prefix)
    return dict((
        (key[prefix_length:], value)
        for key, value in adict.items()
        if key.startswith(prefix)
    ))


def split_keys(adict, separator='.', maxsplit=None):
    """
    This function is best explained by an example::

        d['some.very.long.key'] = 'value'
        split_keys(d)['some']['very']['long']['key']  # 'value'


    It splits all keys in `adict` by `separator`, then for each part of the
    split key but the last it inserts an inner dictionary into the result.

    .. warning:: The function assumes that all keys in `adict` are strings.

    If `maxsplit` is passed, then keys would be split at most `maxsplit` times.

    .. note:: If `maxsplit` is `N` then the keys would be split on at most
        `N+1` parts.
    """
    result = {}
    if maxsplit:
        split = lambda x: x.split(separator, maxsplit)
    else:
        split = lambda x: x.split(separator)
    for key, value in adict.items():
        parts = split(key)
        container = result
        for part in parts[:-1]:
            container = container.setdefault(part, dict())
        container[parts[-1]] = value
    return result

__all__ = (
    'filter_by_prefix',
    'parse_keyvalue_pairs',
    'parse_multiline',
    'split_keys',
)
