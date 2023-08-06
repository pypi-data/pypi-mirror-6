API
===

.. module:: ticktock

.. data:: DEFAULT_MAXSIZE

    The default maximum size used in LRU container size management. Currently,
    the default is 300.

.. data:: DEFAULT_TIMEOUT

    The default timeout value used in data expiration. Currently, the default
    is 300 (5 minutes).

.. autoclass:: LRUShelf(dict, protocol=None, writeback=False, keyencoding='utf-8', maxsize=300)
    :members:

    :attr:`maxsize` The maximum size allowed by the LRU cache management features.
    This can be changed directly.

.. autoclass:: TimeoutShelf(dict, protocol=None, writeback=False, keyencoding='utf-8', timeout=300)
    :members: set, settimeout, sync

    :attr:`timeout` The default timeout value in seconds for this container.
    This value can be changed directly. It can also be overridden as needed by
    calling :meth:`settimeout`.

.. autoclass:: LRUTimeoutShelf(dict, protocol=None, writeback=False, keyencoding='utf-8', maxsize=300, timeout=300)
    :members: set, settimeout, sync

    :attr:`maxsize` The maximum size allowed by the LRU cache management features.
    This can be changed directly.

    :attr:`timeout` The default timeout value in seconds for this container.
    This value can be changed directly. It can also be overridden as needed by
    calling :meth:`settimeout`.

.. autofunction:: open
