Tick Tock
=========

Tick Tock adds least-recently-used cache management and automatic data timeout
to Python's
`Shelf <http://docs.python.org/3.3/library/shelve.html#shelve.Shelf>`_ class.

.. code:: python

    >>> # Make your shelves manage your data based on time and/or size:
    ... myshelf = ticktock.open('myshelf', timeout=60, maxsize=50)

    >>> myshelf['foo'] = 'value'
    >>> myshelf['foo']
    'value'
    >>> # Wait 60 seconds, then try again:
    ... myshelf['foo']
        ...
        KeyError: 'foo'
    
    >>> len(myshelf)
    50
    >>> myshelf['bar'] = 'value'
    >>> # Adding 'bar' kicks the least-recently-used key off the Shelf
    ... len(myshelf)
    50

Install
-------

Tick Tock supports Python 2.6, 2.7, and 3.

To install, use pip:

.. code:: bash

    $ pip install ticktock

Documentation
-------------

`Tick Tock's documentation <https://ticktock.readthedocs.org/>`_ contains a
gentle introduction along with a complete API overview. For more information
on how to get started with Tick Tock, this is where you should look.

Bug/Issues Tracker
------------------

Tick Tock uses its
`GitHub Issues page <https://github.com/tsroten/ticktock/issues>`_ to track
bugs, feature requests, and support questions.

License
-------

Tick Tock is released under the OSI-approved
`MIT License <http://opensource.org/licenses/MIT>`_. See the file
``LICENSE.txt`` for more information.
