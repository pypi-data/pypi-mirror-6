Installation
============

Installing Tick Tock is easy. There are no third-party dependencies. As long
as you have Python 2.6, 2.7 or 3, Tick Tock should run just fine.

Pip
---

To keep things simple, install Tick Tock using
`pip <http://www.pip-installer.org/>`_:

.. code-block:: bash

    $ pip install ticktock

This will download Tick Tock from
`the Python Package Index <http://pypi.python.org/>`_ and install it in your
Python's ``site-packages`` directory.

Tarball Release
---------------

If you'd rather install Tick Tock manually:

1.  Download the most recent release from `Tick Tock's PyPi page <http://pypi.python.org/pypi/ticktock/>`_.
2. Unpack the tarball.
3. From inside the directory ``ticktock-XX``, run ``python setup.py install``

This will install Tick Tock in your Python's ``site-packages`` directory.

Install the Development Version
-------------------------------

`Tick Tock's code <https://github.com/tsroten/ticktock>`_ is hosted at GitHub.
To install the development version first make sure `Git <http://git-scm.org/>`_
is installed. Then run:

.. code-block:: bash
   
    $ git clone git://github.com/tsroten/ticktock.git
    $ pip install -e ticktock

This will link the ``ticktock`` directory into your ``site-packages``
directory.

Running the Tests
-----------------

Running the tests is easy:

.. code-block:: bash

    $ python setup.py test

If you want to run the tests using different versions of Python, install and
run tox:

.. code-block:: bash

    $ pip install tox
    $ tox
