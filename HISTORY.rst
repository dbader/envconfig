.. :changelog:

History
-------

Unreleased
++++++++++

- Add ``envconfig.json()`` for structured values.
- Require Python 3.9+. Python 3.8 has been end-of-life since October 2024
  and the setuptools release needed for SPDX license metadata does not
  support it.
- Use an SPDX license expression in ``pyproject.toml``.

0.3.0 (2026-09-06)
++++++++++++++++++

- Drop Python 2; require Python 3.8+. Package metadata moved to
  ``pyproject.toml``. CI moved from Travis to GitHub Actions.
- Add keyword-only ``default=`` to every reader. Defaults apply only when
  the variable is missing: an empty string is still parsed as a value and
  an invalid value still raises.
- Add ``envconfig.float()``.
- Add ``strip=``, ``allow_blank=`` and ``unescape_newlines=`` keyword
  arguments to ``envconfig.str()``. Default behaviour is unchanged.
- Add ``EnvConfigError``, ``MissingError`` (a ``KeyError``) and
  ``InvalidError`` (a ``ValueError``). Error messages now always name the
  variable and the expected format and no longer include the raw value.
- ``bool()`` additionally accepts ``on`` / ``off``.
- ``list()``: whitespace-only items are now dropped like empty ones, so
  ``"a, ,b"`` yields ``["a", "b"]`` (previously ``["a", "", "b"]``).
- ``dict()``: items are split on the first key/value separator only, so
  ``"url:https://example.com"`` now parses instead of raising.
- ``dict()``: empty keys and duplicate keys now raise ``InvalidError``
  (previously an empty key was accepted and the last duplicate won).
- Add type annotations and a ``py.typed`` marker.

0.2.1 (2021-07-23)
++++++++++++++++++

- envconfig.list(): return [] if env var is empty
- envconfig.dict(): return {} if env var is empty

0.2.0 (2021-07-23)
++++++++++++++++++

- Add envconfig.dict()


0.1.0 (2013-05-27)
++++++++++++++++++

- Initial release
