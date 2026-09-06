"""Read typed configuration values from the process environment.

Compared to using ``os.environ`` directly this module provides a few
strict, convenience readers, for example, for parsing booleans.

Every reader raises a clear error when a variable is missing or
malformed instead of silently falling back to a wrong value. Explicit
defaults are supported via a keyword-only ``default`` argument and are
used *only* when the variable is absent from the environment.

-- Daniel
"""

from __future__ import annotations

import builtins
import os
from typing import Any, Dict, List, Sequence, TypeVar, Union, overload

__all__ = [
    "EnvConfigError",
    "MissingError",
    "InvalidError",
    "str",
    "bool",
    "int",
    "float",
    "list",
    "dict",
]

__version__ = "0.3.0"

# We intentionally shadow the builtin type names so that the function name
# matches the Python type it returns, e.g. envconfig.str() returns a str,
# envconfig.int() returns an int, and so on. Internally we always go through
# the ``builtins`` module. pylint: disable=redefined-builtin

T = TypeVar("T")


class _Missing:
    """Sentinel type used to tell "no default given" apart from ``None``."""

    __slots__ = ()

    def __repr__(self) -> builtins.str:
        return "envconfig.MISSING"


MISSING = _Missing()
_Default = Union[T, _Missing]


class EnvConfigError(Exception):
    """Base class for all errors raised by envconfig."""

    def __init__(self, name: builtins.str, message: builtins.str) -> None:
        super().__init__(message)
        self.name = name
        self.message = message

    def __str__(self) -> builtins.str:
        return self.message


class MissingError(EnvConfigError, KeyError):
    """A required environment variable is not set.

    Subclasses ``KeyError`` for compatibility with envconfig < 0.3.
    """

    def __init__(self, name: builtins.str) -> None:
        super().__init__(
            name,
            f"Missing environment variable {name}. "
            "Please check your environment variables.",
        )


class InvalidError(EnvConfigError, ValueError):
    """An environment variable is set but cannot be parsed.

    Subclasses ``ValueError`` for compatibility with envconfig < 0.3.

    The raw value is deliberately not included in the message so that
    secrets do not leak into logs or tracebacks.
    """

    def __init__(self, name: builtins.str, expected: builtins.str) -> None:
        super().__init__(
            name, f"Invalid environment variable {name}: expected {expected}."
        )
        self.expected = expected


def _raw(name: builtins.str) -> Union[builtins.str, _Missing]:
    """Return the raw value of ``name`` or ``MISSING`` if it is not set."""
    try:
        return os.environ[name]
    except KeyError:
        return MISSING


@overload
def str(
    name: builtins.str,
    *,
    strip: builtins.bool = ...,
    allow_blank: builtins.bool = ...,
) -> builtins.str: ...


@overload
def str(
    name: builtins.str,
    *,
    default: T,
    strip: builtins.bool = ...,
    allow_blank: builtins.bool = ...,
) -> Union[builtins.str, T]: ...


def str(
    name: builtins.str,
    *,
    default: _Default[Any] = MISSING,
    strip: builtins.bool = True,
    allow_blank: builtins.bool = True,
) -> Any:
    """Return the string value of the environment variable ``name``.

    The value is whitespace-stripped unless ``strip=False``. With
    ``allow_blank=False`` an empty (or, when stripping, whitespace-only)
    value raises ``InvalidError``.

    Raises ``MissingError`` if the variable is not set and no ``default``
    was given. An empty string is a present value and never triggers the
    default.
    """
    value = _raw(name)
    if isinstance(value, _Missing):
        if isinstance(default, _Missing):
            raise MissingError(name)
        return default
    if strip:
        value = value.strip()
    if not allow_blank and not value:
        raise InvalidError(name, "a non-empty string")
    return value


# The following values are accepted when parsing booleans using the
# envconfig.bool() function. All other values raise InvalidError.
_TRUTH_VALUES_TRUE: Sequence[builtins.str] = ("1", "yes", "true", "on")
_TRUTH_VALUES_FALSE: Sequence[builtins.str] = ("0", "no", "false", "off")


@overload
def bool(name: builtins.str) -> builtins.bool: ...


@overload
def bool(name: builtins.str, *, default: T) -> Union[builtins.bool, T]: ...


def bool(name: builtins.str, *, default: _Default[Any] = MISSING) -> Any:
    """Return the boolean value of the environment variable ``name``.

    Accepted values (case-insensitive) are ``1``, ``yes``, ``true``, ``on``
    for ``True`` and ``0``, ``no``, ``false``, ``off`` for ``False``.
    Anything else raises ``InvalidError``.
    """
    value = str(name, default=default)
    if not isinstance(value, builtins.str):
        return value
    normalized = value.lower()
    if normalized in _TRUTH_VALUES_TRUE:
        return True
    if normalized in _TRUTH_VALUES_FALSE:
        return False
    raise InvalidError(
        name,
        "a boolean (one of {} for true, or {} for false)".format(
            ", ".join(_TRUTH_VALUES_TRUE), ", ".join(_TRUTH_VALUES_FALSE)
        ),
    )


@overload
def int(name: builtins.str) -> builtins.int: ...


@overload
def int(name: builtins.str, *, default: T) -> Union[builtins.int, T]: ...


def int(name: builtins.str, *, default: _Default[Any] = MISSING) -> Any:
    """Return the integer value of the environment variable ``name``."""
    value = str(name, default=default)
    if not isinstance(value, builtins.str):
        return value
    try:
        return builtins.int(value)
    except ValueError:
        raise InvalidError(name, "an integer") from None


@overload
def float(name: builtins.str) -> builtins.float: ...


@overload
def float(name: builtins.str, *, default: T) -> Union[builtins.float, T]: ...


def float(name: builtins.str, *, default: _Default[Any] = MISSING) -> Any:
    """Return the float value of the environment variable ``name``."""
    value = str(name, default=default)
    if not isinstance(value, builtins.str):
        return value
    try:
        return builtins.float(value)
    except ValueError:
        raise InvalidError(name, "a number") from None


@overload
def list(name: builtins.str, separator: builtins.str = ...) -> List[builtins.str]: ...


@overload
def list(
    name: builtins.str, separator: builtins.str = ..., *, default: T
) -> Union[List[builtins.str], T]: ...


def list(
    name: builtins.str,
    separator: builtins.str = ",",
    *,
    default: _Default[Any] = MISSING,
) -> Any:
    """Return a list of strings from the environment variable ``name``.

    The value is split on ``separator``. Items are whitespace-stripped and
    empty items are dropped, so ``"a, ,b"`` and ``"a,,b"`` both yield
    ``["a", "b"]``. An empty variable yields ``[]``.
    """
    value = str(name, default=default)
    if not isinstance(value, builtins.str):
        return value
    items = (item.strip() for item in value.split(separator))
    return [item for item in items if item]


@overload
def dict(
    name: builtins.str,
    item_separator: builtins.str = ...,
    key_value_separator: builtins.str = ...,
) -> Dict[builtins.str, builtins.str]: ...


@overload
def dict(
    name: builtins.str,
    item_separator: builtins.str = ...,
    key_value_separator: builtins.str = ...,
    *,
    default: T,
) -> Union[Dict[builtins.str, builtins.str], T]: ...


def dict(
    name: builtins.str,
    item_separator: builtins.str = ",",
    key_value_separator: builtins.str = ":",
    *,
    default: _Default[Any] = MISSING,
) -> Any:
    """Return a dictionary of strings from the environment variable ``name``.

    The value is split into items on ``item_separator``; each item is split
    into key and value on the *first* ``key_value_separator``, so values may
    themselves contain the separator (``"url:https://example.com"`` works).
    Keys and values are whitespace-stripped. An empty variable yields ``{}``.

    Raises ``InvalidError`` for an item without a key/value separator, for
    an empty key, or for a key that appears more than once.

    Neither separator can be escaped; for structured values use a different
    format (e.g. JSON) rather than this simple delimiter syntax.
    """
    items = list(name, separator=item_separator, default=default)
    if not isinstance(items, builtins.list):
        return items
    expected = (
        f'key/value pairs like "key{key_value_separator}value" '
        f'separated by "{item_separator}"'
    )
    result: Dict[builtins.str, builtins.str] = {}
    for item in items:
        key, sep, value = item.partition(key_value_separator)
        key = key.strip()
        if not sep or not key:
            raise InvalidError(name, expected)
        if key in result:
            raise InvalidError(name, expected + " with unique keys")
        result[key] = value.strip()
    return result
