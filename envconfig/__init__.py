"""A module for reading values from the process's environment variables.

Compared to using straight os.getenv() this module provides a view
convenience functions, for example, for parsing booleans.

I was not happy with using straight os.getenv() because we've had a
number of errors that were related to missing config values in .env
files. This module should help with that by providing a clean way for
accessing config variables.

-- Daniel
"""

import os
try:
    import builtins
except ImportError:
    import __builtin__ as builtins

# Silence "shadows a builtin with same name" messages. We're intentionally
# doing this to let the method name match the Python datatype, e.g. str()
# returns a str, int() returns a Python int and so on.
# pylint: disable-msg=W0622


def str(name):
    """Return the string value of the config variable `name`.
    Raises KeyError if the given name does not exist.
    """
    try:
        value = builtins.str(os.environ[name]).strip()
        return value
    except KeyError:
        raise KeyError('Missing config key "%s". '
                       'Please check your environment variables.' % name)

# The following values are accepted when parsing booleans using the
# config.bool() function. All other values raise a ValueError.
_TRUTH_VALUES_TRUE = ['1', 'yes', 'true']
_TRUTH_VALUES_FALSE = ['0', 'no', 'false']


def bool(name):
    """Return the bool value of the config variable `name`."""
    value = str(name).strip().lower()
    if value in _TRUTH_VALUES_TRUE:
        return True
    elif value in _TRUTH_VALUES_FALSE:
        return False
    raise ValueError('Cannot parse boolean config key "%s": '
                     'Unknown value "%s". '
                     'Allowed values for "True" are %s. '
                     'Allowed values for "False" are %s.'
                     % (name, value, _TRUTH_VALUES_TRUE, _TRUTH_VALUES_FALSE))


def int(name):
    """Return the int value of the config variable `name`."""
    return builtins.int(str(name))


def list(name, separator=','):
    """Return a list of strings from the config variable `name`.
    The individual list elements are whitespace-stripped.
    """
    return [item.strip() for item in str(name).split(separator)]
