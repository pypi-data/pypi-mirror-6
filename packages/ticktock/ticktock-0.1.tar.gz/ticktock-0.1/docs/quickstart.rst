Quickstart
==========

This page will introduce you to Tick Tock's general usage. If you haven't
installed Tick Tock yet, read :doc:`installation`.

Create a Shelf
--------------

Tick Tock adds features to Python's built-in :class:`~shelve.Shelf` class. A
shelf is a persistent dictionary-like object. For example, you can use it as a
cache or simply a persistent storage container. Be sure to read the Python
documentation on the :mod:`shelve` module if you want to learn more about how
shelves work.

We'll start by creating a shelf using :meth:`ticktock.open`:

.. code-block:: python

    >>> import ticktock
    >>> shelf = ticktock.open('my_cache', maxsize=500, timeout=300)

The newly created instance of :class:`~ticktock.LRUTimeoutShelf` uses
:mod:`dbm` as a backend and supports
`least-recently-used <http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used>`_
(LRU) cache management and automatic data expiration.

.. TIP::
    If you don't need LRU cache management or data timeout features, set
    the corresponding keyword argument to :data:`None`. Doing so will disable
    those features.


Use a Shelf
-----------

Because our newly created shelf inherits from :class:`~shelve.Shelf`, you can
use it just like a normal shelf (which emulates :class:`dict`):

.. code-block:: python

    >>> shelf['foo'] = 'value'  # set a value
    >>> shelf['foo']            # get a value
    'value'
    >>> del shelf['foo']        # delete a value

    >>> # shelves can store any picklable value
    ... shelf['bar'] = ['like', 'lists!']
    >>> shelf['bar']
    ['like', 'lists!']

    >>> # but keys must be strings
    ... shelf[1] = 'foo'
        ...
        AttributeError: 'int' object has no attribute 'encode'

Data Timeout
~~~~~~~~~~~~

Now watch your data expire:

.. code-block:: python

    >>> import time
    >>> shelf['foo'] = expensive_func('foo', 35)
    >>> shelf['foo']
    'This took forever to compute! Thank goodness I have a cache.'
    >>> time.sleep(300)  # wait for 5 minutes
    >>> shelf['foo']
        ...
        KeyError: 'foo'

You can use this feature to your advatange by using
:meth:`~ticktock.LRUTimeoutShelf.set`:

.. code-block:: python

    >>> shelf.set('foo', expensive_func, 'foo', 35)
    'This took forever to compute! Thank goodness I have a cache.'
    >>> # let it expire and try again:
    ... time.sleep(300)  # wait for 5 minutes
    >>> shelf.set('foo', expensive_func, 'foo', 35)
    'This important value has changed! Good thing I can cache it again.'

:meth:`~ticktock.LRUTimeoutShelf.set` will return the
value of the key if it exists. If it doesn't, then the given function is
called with the passed arguments and that value is stored and returned.

If you need to override the shelf's timeout value, you can call
:meth:`~ticktock.LRUTimeoutShelf.settimeout`:

.. code-block:: python

    >>> shelf.settimeout('short timeout', 'only 5 seconds!', 5)
    >>> shelf['short_timeout']
    'only 5 seconds!'
    >>> time.sleep(5)
    >>> shelf['short_timeout']
        ...
        KeyError: 'short_timeout'

LRU Cache Management
~~~~~~~~~~~~~~~~~~~~

If your shelf grows to large, the shelf will manage itself:

.. code-block:: python

    >>> len(shelf)
    500
    >>>shelf['key'] = 'value'
    >>> # the least-recently-used item was discarded
    ... len(shelf)
    500

Syncing the In-Memory Shelf Copy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you perform any operations on mutable entries, a call to
:meth:`Shelf.sync <shelve.Shelf.sync>` is necessary to write the changes to
disk. When you close a shelf (see below),
:meth:`Shelf.sync <shelve.Shelf.sync>` is called automatically.

.. code-block:: python

    >>> shelf['bar'].extend(['and tuples!', ('t', 'u', 'p', 'l', 'e')])
    >>> shelf['bar']
    ['like', 'lists!', 'and tuples!', ('t', 'u', 'p', 'l', 'e')]
    >>> # currently, this extend only affects the shelf's in-memory copy
    ... # call sync() to write back the changes
    ... shelf.sync()


Close a Shelf
-------------

Shelves need to be closed via :meth:`Shelf.close <shelve.Shelf.close>`:

.. code-block:: python

    >>> shelf.close()

Closing a shelf syncs any changes from the in-memory copy to the backend. It
also closes the associated backend container.


Data Persistence
----------------

Shelf data is persistent. This means that once you close a shelf, you can open
it up again and your data will still be there. Simply open a shelf with the
same target file:

.. code-block:: python

    >>> shelf = ticktock.open('cache_dir', maxsize=500, timeout=300)
    >>> shelf['bar']
    ['like', 'lists!', 'and tuples!', ('t', 'u', 'p', 'l', 'e')]
