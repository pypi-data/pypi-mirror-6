Changes
=======

1.1 (2014-02-27)
----------------

Features:

- A queue is now also a context manager, providing transactional
  semantics.

- A queues now returns task objects which provide metadata and allows
  reading and writing task data.

Improvements:

- The same connection pool can now be used with different queues.

Bugs:

- The `Literal` string wrapper did not work correctly with `psycopg2`.

- The transaction manager now correctly returns connections to the
  pool.


1.0 (2013-11-20)
----------------

- Initial public release.
