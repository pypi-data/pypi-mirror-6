"""Adds LRU cache management and automatic data timeout to Python's Shelf.

Classes:
    LRUShelf: A shelf with LRU cache management.
    TimeoutShelf: A shelf with automatic data timeout features.
    LRUTimeoutShelf: A shelf with LRU cache management and data timeout.

Functions:
    open: Open a database file as a persistent dictionary.

"""
from collections import deque
from shelve import Shelf
import sys
from time import time

is_py3 = sys.version_info[0] > 2

DEFAULT_MAXSIZE = 300
DEFAULT_TIMEOUT = 300  # 5 minutes


class _LRUMixin(object):
    """Adds LRU cache management to containers, e.g. :class:`~shelve.Shelf`.

    This mixin will keep a container under a given size by discarding the
    least recently used items when the container overflows.

    .. NOTE::
        The queue that keeps track of which keys are the least recently used
        is not stored in the container itself. This means that even if the
        container is persistent, the LRU queue will not persist with the data.

    For this mixin to work well, all dict methods that involve setting a key,
    getting a value, or deleting a key need to be routed through this class'
    :meth:`__setitem__`, :meth:`__getitem__`, and :meth:`__delitem__`. The
    built-in dict class won't do this by default, so it is better to inherit
    from UserDict if you want to make a custom dictionary. If you subclass
    dict, you might want to also inherit from
    :class:`~collections.abc.MutableMapping` so the _LRUMixin will work
    properly. Otherwise, you will need to manually code methods such as
    ``update()``, ``copy()``, ``keys()``, ``values()``, etc. So, it's best to
    stick with :class:`~collections.abc.MutableMapping` or
    :class:`~collections.UserDict` if possible.

    """

    def __init__(self, *args, **kwargs):
        """Initialize LRU size management for a container.

        Keyword arguments:
            maxsize: The maximum size the container should be. Defaults to
                module-level DEFAULT_MAXSIZE.

        """
        self.maxsize = kwargs.get('maxsize', DEFAULT_MAXSIZE)
        if 'maxsize' in kwargs:
            del kwargs['maxsize']
        if self.maxsize is None:
            raise TypeError("maxsize must be a non-negative integer")
        super(_LRUMixin, self).__init__(*args, **kwargs)
        self._queue = deque()          # create a queue of keys
        for key in list(self.keys()):  # populate queue with existing keys
            self._remove_add_key(key)

    def _remove_add_key(self, key):
        """Move a key to the end of the linked list and discard old entries."""
        if not hasattr(self, '_queue'):
            return  # haven't initialized yet, so don't bother
        if key in self._queue:
            self._queue.remove(key)
        self._queue.append(key)
        if self.maxsize == 0:
            return
        while len(self._queue) > self.maxsize:
            del self[self._queue[0]]

    def __getitem__(self, key):
        value = super(_LRUMixin, self).__getitem__(key)
        self._remove_add_key(key)
        return value

    def __setitem__(self, key, value):
        super(_LRUMixin, self).__setitem__(key, value)
        self._remove_add_key(key)

    def __delitem__(self, key):
        super(_LRUMixin, self).__delitem__(key)
        if hasattr(self, '_queue'):
            self._queue.remove(key)


class _TimeoutMixin(object):
    """A mixin that adds automatic data timeout to mapping containers.

    If you try to access an expired key, a KeyError will be raised, just like
    when you try to access a non-existent key.

    For this mixin to work well, all dict methods that involve setting a key,
    getting a value, deleting a key, iterating over the container, or getting
    the length or formal representation need to be routed through this class'
    :meth:`__setitem__`, :meth:`__getitem__`, :meth:`__delitem__`,
    :meth:`__iter__`, :meth:`__len__`, and :meth:`__repr__`. The built-in dict
    class won't do this by default, so it is better to inherit from
    :class:`~collections.UserDict` if you want to make a custom dictionary. If
    you subclass dict, you might want to also inherit from
    :class:`~collections.abc.MutableMapping` so the _TimeoutMixin will work
    properly. Otherwise, you will need to manually code methods such as
    ``update()``, ``copy()``, ``keys()``, ``values()``, etc. So, it's
    best to stick with :class:`~collections.abc.MutableMapping` or
    :class:`~collections.UserDict` if possible.

    Attributes:
        timeout: The default timeout value in seconds.
            A zero means that keys won't timeout by default.
        _index: The timeout index mapping (maps keys to timeout values).
        _INDEX: The key name used for the timeout index.

    """

    #: The timeout index key name. This key is considered protected and access
    #: to it is blocked.
    _INDEX = 'f1dd04ff3d4d9adfabd43a3f9fda9b4b78302b21'

    def __init__(self, *args, **kwargs):
        """Initialize the timeout features of the mapping container.

        After calling the base class' __init__() method, the timeout index
        is read from the container or created if it doesn't exist. Then, any
        existing expired values are deleted.

        Keyword arguments:
            timeout: The default timeout value in seconds to use. If
                not present, the module-level constant timeout value
                is used.

        """
        self.timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)
        if 'timeout' in kwargs:
            del kwargs['timeout']
        if self.timeout is None:
            raise TypeError("timeout must be a non-negative integer")
        super(_TimeoutMixin, self).__init__(*args, **kwargs)
        try:
            self._index = super(_TimeoutMixin, self).__getitem__(self._INDEX)
        except KeyError:
            self._index = {}
            super(_TimeoutMixin, self).__setitem__(self._INDEX, self._index)
        else:
            for key in self:
                self._is_expired(key)

    def _is_expired(self, key):
        """Check if a key is expired. If so, delete the key."""
        if not hasattr(self, '_index'):
            return False  # haven't initalized yet, so don't bother
        timeout = self._index[key]
        if timeout is None or timeout >= time():
            return False
        del self[key]  # key expired, so delete it from container
        return True

    def __getitem__(self, key):
        if key == self._INDEX:
            raise KeyError("cannot access protected key '%s'" % self._INDEX)
        try:
            if not self._is_expired(key):
                return super(_TimeoutMixin, self).__getitem__(key)
        except KeyError:
            pass
        raise KeyError(key)

    def set(self, key, func, *args, **kwargs):
        """Return key's value if it exists, otherwise call given function.

        :param key: The key to lookup/set.
        :param func: A function to use if the key doesn't exist.

        All other arguments and keyword arguments are passed to *func*.

        """
        if key in self:
            return self[key]
        self[key] = value = func(*args, **kwargs)
        return value

    def settimeout(self, key, value, timeout):
        """Set a key with a timeout value (in seconds).

        :meth:`settimeout` is used to override the shelf's timeout value.

        :param timeout: The timeout value in seconds for the given key.
            ``0`` means that the key will never expire.
        :type timeout: integer

        """
        self[key] = value
        if not hasattr(self, '_index'):
            return  # don't update index if __init__ hasn't completed
        self._index[key] = int(time() + timeout) if timeout else None

    def __setitem__(self, key, value):
        if key == self._INDEX:
            raise TypeError("reserved key name '%s'" % self._INDEX)
        super(_TimeoutMixin, self).__setitem__(key, value)
        if not hasattr(self, '_index'):
            return  # don't update index if __init__ hasn't completed
        self._index[key] = int(time() + self.timeout) if self.timeout else None

    def __delitem__(self, key):
        if key == self._INDEX:
            raise KeyError("cannot delete protected key '%s'" % self._INDEX)
        super(_TimeoutMixin, self).__delitem__(key)
        if not hasattr(self, '_index'):
            return  # don't update index if __init__ hasn't completed
        del self._index[key]

    def __iter__(self):
        for key in super(_TimeoutMixin, self).__iter__():
            if key == self._INDEX:
                continue
            if not self._is_expired(key):
                yield key

    def __contains__(self, key):
        """Hide the timeout index from __contains__."""
        if key == self._INDEX:
            return False
        return super(_TimeoutMixin, self).__contains__(key)

    def __len__(self):
        """Hide the timeout index from the object's length."""
        return super(_TimeoutMixin, self).__len__() - 1

    def __repr__(self):
        """Remove the timeout index from the object representation."""
        for key in self:  # delete expired data via __iter__()
            pass
        super(_TimeoutMixin, self).__delitem__(self._INDEX)  # hide the index
        _repr = super(_TimeoutMixin, self).__repr__()
        super(_TimeoutMixin, self).__setitem__(self._INDEX, self._index)
        return _repr

    def sync(self):
        """Sync the timeout index entry with the shelf."""
        super(_TimeoutMixin, self).__setitem__(self._INDEX, self._index)
        super(_TimeoutMixin, self).sync()

    def __del__(self):
        """Sync timeout index when object is deleted."""
        super(_TimeoutMixin, self).__setitem__(self._INDEX, self._index)
        super(_TimeoutMixin, self).__del__()

    def __exit__(self, *exc_info):
        """Sync timeout index on exit."""
        self.sync()
        super(_TimeoutMixin, self).__exit__(*exc_info)


class _NewOldMixin(object):
    """Makes certain dict methods follow MRO to the container."""

    def __init__(self, *args, **kwargs):
        self._class = kwargs.pop('old_class')
        self._class.__init__(self, *args, **kwargs)

    def __getitem__(self, key):
        return self._class.__getitem__(self, key)

    def __setitem__(self, key, value):
        return self._class.__setitem__(self, key, value)

    def __delitem__(self, key):
        return self._class.__delitem__(self, key)

    def __iter__(self):
        return self._class.__iter__(self)

    def __len__(self):
        return self._class.__len__(self)


class LRUShelf(_LRUMixin, _NewOldMixin, Shelf):
    """A :class:`~shelve.Shelf` with LRU cache management.

    .. NOTE::
        The *keyencoding* keyword argument is only used in Python 3.

    """

    def __init__(self, *args, **kwargs):
        """Initialize LRU cache management.

        :param maxsize: The maximum size the container is allowed to grow to.
            ``0`` means that no size limit is enforced.
        :type maxsize: integer

        """
        super(LRUShelf, self).__init__(*args, old_class=Shelf, **kwargs)


class TimeoutShelf(_TimeoutMixin, _NewOldMixin, Shelf):
    """A :class:`~shelve.Shelf` with automatic data timeout.

    .. NOTE::
        The *keyencoding* keyword argument is only used in Python 3.

    """

    def __init__(self, *args, **kwargs):
        """Initialize the data timeout index.

        :param timeout: The default timeout value for data (in seconds). ``0``
            means that the data never expires.
        :type timeout: integer

        """
        super(TimeoutShelf, self).__init__(*args, old_class=Shelf, **kwargs)

    if not is_py3:
        def keys(self):
            """Override :meth:`~shelve.Shelf.keys` to hide timeout index.

            This also removes expired keys.

            """
            _keys = self.dict.keys()
            if self._INDEX in _keys:
                _keys.remove(self._INDEX)
            keys = []
            for key in _keys:
                if not self._is_expired(key):
                    keys.append(key)
            return keys


class LRUTimeoutShelf(_LRUMixin, TimeoutShelf):
    """A :class:`~shelve.Shelf` with LRU cache management and data timeout.

    .. NOTE::
        The *keyencoding* keyword argument is only used in Python 3.

    """

    def __init__(self, *args, **kwargs):
        """Initialize LRU cache management and data timeout index.

        :param maxsize: The maximum size the container is allowed to grow to.
            ``0`` means that no size limit is enforced.
        :type maxsize: integer
        :param timeout: The default timeout value for data (in seconds). ``0``
            means that the data never expires.
        :type timeout: integer

        """
        super(LRUTimeoutShelf, self).__init__(*args, **kwargs)


def open(filename, flag='c', protocol=None, writeback=False,
         maxsize=DEFAULT_MAXSIZE, timeout=DEFAULT_TIMEOUT):
    """Open a database file as a persistent dictionary.

    The persistent dictionary file is opened using :func:`dbm.open`, so
    performance will depend on which :mod:`dbm` modules are installed.

    :func:`open` chooses to open a :class:`Shelf <shelve.Shelf>`,
    :class:`LRUShelf`, :class:`TimeoutShelf`, or :class:`LRUTimeoutShelf`
    depending on the values of keyword arguments *maxsize* and *timeout*.
    A :data:`None` value for *maxsize* and *timeout* will disable the LRU
    cache management and automatic data timeout features respectively.

    :param filename: The base filename for the underlying database that is
        passed to :func:`dbm.open`.
    :param flag: The flag to pass to :func:`dbm.open`.
    :param protocol: The pickle protocol to pass to :func:`pickle.dump`.
    :param writeback: Whether or not to write back all accessed entries on
        :meth:`Shelf.sync <shelve.Shelf.sync>` and
        :meth:`Shelf.close <shelve.Shelf.close>`
    :type writeback: bool
    :param maxsize: The maximum size the container is allowed to grow to.
        ``0`` means that no size limit is enforced. :data:`None` means that
        LRU cache management is disabled.
    :type maxsize: integer or :data:`None`
    :param timeout: The default timeout value for data (in seconds). ``0``
        means that the data never expires. :data:`None` means that automatic
        timeout features will be disabled.
    :type timeout: integer or :data:`None`
    :return: A shelf
    :rtype: :class:`~shelve.Shelf`, :class:`LRUShelf`, :class:`TimeoutShelf`,
        or :class:`LRUTimeoutShelf`

    """
    import dbm
    dict = dbm.open(filename, flag)
    if maxsize is None and timeout is None:
        return Shelf(dict, protocol, writeback)
    elif maxsize is None:
        return TimeoutShelf(dict, protocol, writeback, timeout=timeout)
    elif timeout is None:
        return LRUShelf(dict, protocol, writeback, maxsize=maxsize)
    return LRUTimeoutShelf(dict, protocol, writeback, timeout=timeout,
                           maxsize=maxsize)
