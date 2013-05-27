envconfig
=========


.. image:: https://api.travis-ci.org/dbader/envconfig.png
        :target: https://travis-ci.org/dbader/envconfig

.. image:: https://coveralls.io/repos/dbader/envconfig/badge.png
        :target: https://coveralls.io/r/dbader/envconfig

.. image:: https://pypip.in/v/envconfig/badge.png
        :target: https://pypi.python.org/pypi/envconfig


Features
--------
- todo

Usage
-----

.. code-block:: bash

    $ pip install envconfig

.. code-block:: python

    import envconfig

    boolopt = envconfig.bool("BOOL_OPTION")
    intopt = envconfig.int("INTEGER_OPTION")
    stropt = envconfig.int("STRING_OPTION")
    listopt = envconfig.list("LIST_OPTION")

Meta
----

Daniel Bader – `@dbader_org <https://twitter.com/dbader_org>`_ – mail@dbader.org

Distributed under the MIT license. See ``LICENSE.txt`` for more information.

https://github.com/dbader/envconfig
