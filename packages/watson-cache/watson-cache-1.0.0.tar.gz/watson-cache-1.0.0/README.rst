Watson-Cache
============

A collection of cache storage mechanisms that act like a dict.

Currently supporting:

-  Memory
-  File
-  Memcache

Also contains a decorator that can be used within the
``watson-framework`` package.

For full documentation please see `Read The
Docs <http://watson-cache.readthedocs.org/>`__.

Build Status
^^^^^^^^^^^^

|Build Status| |Coverage Status| |Version| |Downloads| |Licence|

Installation
------------

``pip install watson-cache``

Dependencies
------------

-  watson-common
-  watson-di (for test coverage, and decorator usage)
-  python3-memcached

Todo
----

-  Add SqlAlchemy based storage
-  Add Redis based storage

.. |Build Status| image:: https://api.travis-ci.org/watsonpy/watson-cache.png?branch=master
   :target: https://travis-ci.org/watsonpy/watson-cache
.. |Coverage Status| image:: https://coveralls.io/repos/watsonpy/watson-cache/badge.png
   :target: https://coveralls.io/r/watsonpy/watson-cache
.. |Version| image:: https://pypip.in/v/watson-cache/badge.png
   :target: https://pypi.python.org/pypi/watson-cache/
.. |Downloads| image:: https://pypip.in/d/watson-cache/badge.png
   :target: https://pypi.python.org/pypi/watson-cache/
.. |Licence| image:: https://pypip.in/license/watson-cache/badge.png
   :target: https://pypi.python.org/pypi/watson-cache/
