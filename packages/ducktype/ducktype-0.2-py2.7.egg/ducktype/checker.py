# -*- coding: utf8 -*-
import inspect

__all__ = ["isducktype"]

def isducktype(given, obj_or_tuple):
    if type(obj_or_tuple) is not tuple:
        obj_or_tuple = (obj_or_tuple, )
    for obj in obj_or_tuple:
        if __is_ducktype(given, obj):
            return True
    return False

def __is_ducktype(given, expected):
    if inspect.isroutine(expected):
        return _cmp_routine(given, expected)
    if hasattr(expected, '__ducktypecheck__'):
        try:
            return expected.__ducktypecheck__(given)
        except TypeError:
            pass
    return _cmp_obj(given, expected)


_public = lambda member_name: member_name[0] != '_'

def _cmp_obj(given, expected):
    expected_members = filter(_public, dir(expected))
    for member in expected_members:
        if _cmp_member(member, given, expected) is False:
            return False
    return True

def _cmp_member(name, given, expected):
    if hasattr(given, name) is False: return False
    given = getattr(given, name)
    expected = getattr(expected, name)
    is_routine = inspect.isroutine(expected)
    if inspect.isroutine(given):
        return is_routine and _cmp_routine(given, expected)
    return not is_routine

def _cmp_routine(given, expected):
    result = True
    if inspect.ismethod(given):
        given = given.__func__
    if inspect.ismethod(expected):
        expected = expected.__func__

    given = inspect.getargspec(given)
    expected = inspect.getargspec(expected)
    if _no_varargs_or_keywords(given) and _no_varargs_or_keywords(expected):
        defaults_len_e = 0 if expected.defaults is None else len(expected.defaults)
        defaults_len_g = 0 if given.defaults is None else len(given.defaults)
        max_g = len(given.args)
        min_g = max_g - defaults_len_g
        max_e = len(expected.args)
        min_e = max_e - defaults_len_e
        result = (max_g >= min_e and max_g <= max_e) or (min_g <= max_e and min_g >= min_e)
    return result

def _no_varargs_or_keywords(inspected):
    return inspected.varargs is None and inspected.keywords is None

