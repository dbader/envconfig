envconfig
=========

.. image:: https://github.com/dbader/envconfig/actions/workflows/ci.yml/badge.svg
        :target: https://github.com/dbader/envconfig/actions/workflows/ci.yml

.. image:: https://img.shields.io/pypi/v/envconfig.svg
        :target: https://pypi.org/project/envconfig/

A small, strict module for reading typed configuration values from the
OS environment.

Compared to using ``os.environ`` directly this module provides a few
convenience readers (for booleans, integers, lists, ...) that fail loudly
on missing or malformed values instead of silently falling back to a
wrong one.

I was not happy with using straight ``os.getenv()`` because we've had a
number of errors that were related to missing config values in ``.env``
files. This module should help with that by providing a clean way for
accessing config variables.

Usage
-----

.. code-block:: bash

    $ pip install envconfig

.. code-block:: python

    import envconfig

    SECRET_KEY = envconfig.str("DJANGO_SECRET", allow_blank=False)
    EMAIL_PORT = envconfig.int("EMAIL_SMTP_PORT", default=587)
    EMAIL_USE_TLS = envconfig.bool("EMAIL_SMTP_USE_TLS", default=True)
    TIMEOUT = envconfig.float("REQUEST_TIMEOUT", default=2.5)
    PROVIDERS = envconfig.list("VIDEO_PROVIDERS_ENABLED", default=["bunny"])
    HEADERS = envconfig.dict("EXTRA_HEADERS", default={})
    LIMITS = envconfig.json("RATE_LIMITS", default={"burst": 10})

Readers
-------

All readers take the variable name as the first argument and an optional
keyword-only ``default``.

``envconfig.str(name, *, default=..., strip=True, allow_blank=True, unescape_newlines=False)``
    Returns the string value. Whitespace is stripped unless
    ``strip=False``. Pass ``allow_blank=False`` to reject empty values.
    Pass ``unescape_newlines=True`` to turn literal ``\n`` sequences into
    real newlines, for multi-line values such as PEM keys stored on one
    line in ``.env`` files:

    .. code-block:: python

        PADDLE_PUBLIC_KEY = envconfig.str(
            "PADDLE_PUBLIC_KEY", default="", unescape_newlines=True
        )

``envconfig.bool(name, *, default=...)``
    Accepts (case-insensitively) ``1``, ``yes``, ``true``, ``on`` for
    ``True`` and ``0``, ``no``, ``false``, ``off`` for ``False``. Anything
    else, including typos like ``tru``, is an error.

``envconfig.int(name, *, default=...)`` / ``envconfig.float(name, *, default=...)``
    Parses a number with the builtin ``int()`` / ``float()``.

``envconfig.list(name, separator=",", *, default=...)``
    Splits on ``separator``; items are whitespace-stripped and empty items
    are dropped, so ``"a, ,b"`` yields ``["a", "b"]``. An empty variable
    yields ``[]``.

``envconfig.dict(name, item_separator=",", key_value_separator=":", *, default=...)``
    Parses ``"key1:val1,key2:val2"``. Each item is split on the *first*
    ``key_value_separator`` so values may contain it
    (``"url:https://example.com"`` works). Empty keys and duplicate keys
    are errors. Separators cannot be escaped; use ``envconfig.json()``
    for structured values.

``envconfig.json(name, *, default=...)``
    Parses the value as a JSON document and returns the result, typically
    a ``dict`` or ``list``. Use it when values contain separators, need
    nesting, or need non-string types:

    .. code-block:: bash

        RATE_LIMITS='{"burst": 10, "per_minute": 600, "paths": ["/api"]}'

    An empty variable is not valid JSON and raises ``InvalidError``.

Defaults
--------

The contract for ``default`` is deliberately strict:

- Variable missing, no default: ``MissingError`` is raised.
- Variable missing, default given: the default is returned as-is
  (``None`` is a valid default).
- Variable present but invalid: ``InvalidError`` is raised, even if a
  default was given.
- Variable set to an empty string: parsed as an explicit value, never
  replaced by the default. ``str`` returns ``""``, ``list`` returns
  ``[]``, ``dict`` returns ``{}`` and the other readers raise.

Errors
------

``envconfig.MissingError``
    Raised for an unset variable. Subclasses ``KeyError``.

``envconfig.InvalidError``
    Raised for a value that cannot be parsed. Subclasses ``ValueError``.
    Messages name the variable and the expected format but never echo the
    raw value, so secrets do not leak into logs::

        Invalid environment variable EMAIL_SMTP_PORT: expected an integer.

Both derive from ``envconfig.EnvConfigError`` and expose the variable
name as ``.name``.

The package is fully type-annotated and ships a ``py.typed`` marker.
Python 3.9+ is supported.

Releasing
---------

Releases are published to PyPI by GitHub Actions via PyPI trusted
publishing. Bump the version in ``pyproject.toml`` and
``envconfig/__init__.py``, add a ``HISTORY.rst`` entry, merge, then tag:

.. code-block:: bash

    git tag -a v0.3.0 -m "envconfig 0.3.0"
    git push origin v0.3.0

Meta
----

Daniel Bader – `@dbader_org <https://twitter.com/dbader_org>`_ – mail@dbader.org

Distributed under the MIT license. See ``LICENSE.txt`` for more information.

https://github.com/dbader/envconfig
