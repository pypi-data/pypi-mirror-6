==========
GrapheekDB
==========

GrapheekDB is a fast and lightweight Graph Database with various KVS (Key/Value Store) backends :

- Local memory (default backend)
- Kyoto Cabinet : http://fallabs.com/kyotocabinet/
- Symas LMDB : http://symas.com/mdb/

Implementing a new backend for other KVS is quite easy : Local Memory backend is implemented in less that 50 lines of code.

Features :
----------

- nodes (aka vertices) and edges creation and deletion
- nodes and edge lookup (using a django-like syntax)
- path traversal (using a gremlin-like syntax)
- basic nodes & edges indexing feature (works with one or many field)
- aggregation
- speed : path traversal often occurs at 1 million entities/second - thanks to the backends :)
- concurrency : with 1000 concurrent users and simple node creation/deletion, the server can handle 7000 requests/second - thanks to 0mq and gevent

- code base test coverage is currently : 100 %


Installation :
--------------

.. code:: bash

    pip install grapheekdb

Quick intro :
-------------

- A quick introduction is available at : https://bitbucket.org/nidusfr/grapheekdb/src/default/docs/intro.rst

Links:
------

- Home Page : https://bitbucket.org/nidusfr/grapheekdb


