"""Unit tests for envconfig."""

from __future__ import annotations

import os
from typing import Iterator

import pytest

import envconfig

NAME = "ENVCONFIG_TEST_VALUE"


@pytest.fixture(autouse=True)
def clean_env() -> Iterator[None]:
    os.environ.pop(NAME, None)
    yield
    os.environ.pop(NAME, None)


def setenv(value: str) -> None:
    os.environ[NAME] = value


# --- str -------------------------------------------------------------------


def test_str() -> None:
    setenv("Hello, World")
    assert envconfig.str(NAME) == "Hello, World"


def test_str_strips_whitespace_by_default() -> None:
    setenv("  hello  ")
    assert envconfig.str(NAME) == "hello"


def test_str_strip_false_preserves_whitespace() -> None:
    setenv("  hello  ")
    assert envconfig.str(NAME, strip=False) == "  hello  "


def test_str_accepts_blank_by_default() -> None:
    setenv("   ")
    assert envconfig.str(NAME) == ""


def test_str_allow_blank_false_rejects_empty_and_whitespace() -> None:
    setenv("")
    with pytest.raises(envconfig.InvalidError):
        envconfig.str(NAME, allow_blank=False)
    setenv("   ")
    with pytest.raises(envconfig.InvalidError):
        envconfig.str(NAME, allow_blank=False)
    setenv(" x ")
    assert envconfig.str(NAME, allow_blank=False) == "x"


def test_str_allow_blank_false_without_strip() -> None:
    setenv("   ")
    assert envconfig.str(NAME, strip=False, allow_blank=False) == "   "


def test_str_unescape_newlines() -> None:
    setenv("-----BEGIN KEY-----\\nabc\\ndef\\n-----END KEY-----\\n")
    assert envconfig.str(NAME, unescape_newlines=True) == (
        "-----BEGIN KEY-----\nabc\ndef\n-----END KEY-----"
    )


def test_str_unescape_newlines_before_strip() -> None:
    setenv("  x\\n  ")
    assert envconfig.str(NAME, unescape_newlines=True) == "x"
    assert envconfig.str(NAME, unescape_newlines=True, strip=False) == "  x\n  "


def test_str_unescape_newlines_off_by_default() -> None:
    setenv("a\\nb")
    assert envconfig.str(NAME) == "a\\nb"


def test_str_unescape_newlines_with_default() -> None:
    assert envconfig.str(NAME, default="", unescape_newlines=True) == ""


# --- missing / defaults ----------------------------------------------------


def test_missing_raises_missing_error_which_is_a_key_error() -> None:
    with pytest.raises(envconfig.MissingError) as excinfo:
        envconfig.str(NAME)
    assert isinstance(excinfo.value, KeyError)
    assert isinstance(excinfo.value, envconfig.EnvConfigError)
    assert str(excinfo.value) == (
        "Missing environment variable ENVCONFIG_TEST_VALUE. "
        "Please check your environment variables."
    )
    assert excinfo.value.name == NAME


@pytest.mark.parametrize(
    "reader, default",
    [
        (envconfig.str, "fallback"),
        (envconfig.bool, True),
        (envconfig.int, 587),
        (envconfig.float, 1.5),
        (envconfig.list, ["bunny"]),
        (envconfig.dict, {"a": "b"}),
    ],
)
def test_missing_with_default_returns_default(reader, default) -> None:  # type: ignore[no-untyped-def]
    assert reader(NAME, default=default) is default


@pytest.mark.parametrize(
    "reader",
    [
        envconfig.str,
        envconfig.bool,
        envconfig.int,
        envconfig.float,
        envconfig.list,
        envconfig.dict,
    ],
)
def test_none_is_a_valid_default(reader) -> None:  # type: ignore[no-untyped-def]
    assert reader(NAME, default=None) is None


def test_default_must_be_keyword_only() -> None:
    with pytest.raises(TypeError):
        envconfig.int(NAME, 5)  # type: ignore[call-overload]


def test_present_but_invalid_raises_even_with_default() -> None:
    setenv("tru")
    with pytest.raises(envconfig.InvalidError):
        envconfig.bool(NAME, default=False)
    setenv("abc")
    with pytest.raises(envconfig.InvalidError):
        envconfig.int(NAME, default=0)


def test_empty_string_is_an_explicit_value_not_the_default() -> None:
    setenv("")
    assert envconfig.str(NAME, default="fallback") == ""
    assert envconfig.list(NAME, default=["x"]) == []
    assert envconfig.dict(NAME, default={"x": "y"}) == {}
    with pytest.raises(envconfig.InvalidError):
        envconfig.int(NAME, default=1)
    with pytest.raises(envconfig.InvalidError):
        envconfig.bool(NAME, default=True)


# --- bool ------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    ["yes", "1", "YeS", "True", "true", " 1 ", "YES\t", "\tYES\t", "on", "ON"],
)
def test_bool_true(value: str) -> None:
    setenv(value)
    assert envconfig.bool(NAME) is True


@pytest.mark.parametrize("value", ["false", "no", "0", "  NO  ", "False", "off"])
def test_bool_false(value: str) -> None:
    setenv(value)
    assert envconfig.bool(NAME) is False


@pytest.mark.parametrize("value", ["nope", "tru", "", "2", "y", "n", "yes no"])
def test_bool_invalid(value: str) -> None:
    setenv(value)
    with pytest.raises(envconfig.InvalidError) as excinfo:
        envconfig.bool(NAME)
    assert isinstance(excinfo.value, ValueError)
    assert str(excinfo.value).startswith(
        "Invalid environment variable ENVCONFIG_TEST_VALUE: expected a boolean"
    )


# --- int / float -----------------------------------------------------------


def test_int() -> None:
    setenv("12345")
    assert envconfig.int(NAME) == 12345
    setenv(" -7 ")
    assert envconfig.int(NAME) == -7


def test_int_invalid_message_names_variable_and_hides_value() -> None:
    setenv("s3cret-not-a-number")
    with pytest.raises(envconfig.InvalidError) as excinfo:
        envconfig.int(NAME)
    assert str(excinfo.value) == (
        "Invalid environment variable ENVCONFIG_TEST_VALUE: expected an integer."
    )
    assert "s3cret" not in str(excinfo.value)
    assert excinfo.value.name == NAME
    assert excinfo.value.expected == "an integer"


def test_int_rejects_float_strings() -> None:
    setenv("1.5")
    with pytest.raises(envconfig.InvalidError):
        envconfig.int(NAME)


def test_float() -> None:
    setenv("1.5")
    assert envconfig.float(NAME) == 1.5
    setenv("3")
    assert envconfig.float(NAME) == 3.0
    setenv("-1e3")
    assert envconfig.float(NAME) == -1000.0


def test_float_invalid() -> None:
    setenv("abc")
    with pytest.raises(envconfig.InvalidError) as excinfo:
        envconfig.float(NAME)
    assert str(excinfo.value) == (
        "Invalid environment variable ENVCONFIG_TEST_VALUE: expected a number."
    )


# --- list ------------------------------------------------------------------


def test_list() -> None:
    setenv("one,two, three ,four ")
    assert envconfig.list(NAME) == ["one", "two", "three", "four"]


def test_list_custom_separator() -> None:
    setenv("one#two# three #four ")
    assert envconfig.list(NAME, "#") == ["one", "two", "three", "four"]
    assert envconfig.list(NAME, separator="#") == ["one", "two", "three", "four"]


def test_list_empty() -> None:
    setenv("")
    assert envconfig.list(NAME) == []
    setenv("   ")
    assert envconfig.list(NAME) == []


def test_list_drops_blank_items_consistently() -> None:
    setenv("a, ,b")
    assert envconfig.list(NAME) == ["a", "b"]
    setenv("a,,b")
    assert envconfig.list(NAME) == ["a", "b"]
    setenv(",a,b,")
    assert envconfig.list(NAME) == ["a", "b"]


# --- dict ------------------------------------------------------------------


def test_dict() -> None:
    setenv("key1:val1,key2:val2")
    assert envconfig.dict(NAME) == {"key1": "val1", "key2": "val2"}


def test_dict_strips_whitespace() -> None:
    setenv("key1  :  val1 , key2 : val2")
    assert envconfig.dict(NAME) == {"key1": "val1", "key2": "val2"}


def test_dict_custom_separators() -> None:
    setenv("key1#val1,key2#val2")
    assert envconfig.dict(NAME, key_value_separator="#") == {
        "key1": "val1",
        "key2": "val2",
    }
    setenv("key1=val1;key2=val2")
    assert envconfig.dict(NAME, ";", "=") == {"key1": "val1", "key2": "val2"}


def test_dict_empty() -> None:
    setenv("")
    assert envconfig.dict(NAME) == {}


def test_dict_value_may_contain_key_value_separator() -> None:
    setenv("url:https://example.com:8080/x,name:app")
    assert envconfig.dict(NAME) == {
        "url": "https://example.com:8080/x",
        "name": "app",
    }


def test_dict_empty_value_is_allowed() -> None:
    setenv("key:")
    assert envconfig.dict(NAME) == {"key": ""}


@pytest.mark.parametrize(
    "value",
    [
        "key1 s3cret key2 s3cret",  # no separator
        ":s3cret",  # empty key
        "  :s3cret",  # whitespace-only key
        "a:s3cret,a:2",  # duplicate key
        "a:s3cret, a :2",  # duplicate key after stripping
    ],
)
def test_dict_invalid(value: str) -> None:
    setenv(value)
    with pytest.raises(envconfig.InvalidError) as excinfo:
        envconfig.dict(NAME)
    assert isinstance(excinfo.value, ValueError)
    assert str(excinfo.value).startswith(
        "Invalid environment variable ENVCONFIG_TEST_VALUE: expected key/value"
    )
    assert "s3cret" not in str(excinfo.value)


# --- misc ------------------------------------------------------------------


def test_exports() -> None:
    assert envconfig.MISSING is not None
    assert set(envconfig.__all__) == {
        "EnvConfigError",
        "MissingError",
        "InvalidError",
        "str",
        "bool",
        "int",
        "float",
        "list",
        "dict",
    }
    assert isinstance(envconfig.__version__, str)
