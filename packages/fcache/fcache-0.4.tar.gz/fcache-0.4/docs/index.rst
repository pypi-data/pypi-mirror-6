Welcome to fcache
=================

fcache is a dictionary-like, file-based cache module for Python. This is  
fcache's documentation. It covers installation, a tutorial, and the API
reference.

.. NOTE::
    fcache 0.4 is a backwards-incompatible rewrite. fcache's purpose is
    essentially the same, but the API is different.

Installation
------------

Installing fcache is easy. There are no third-party dependencies. As long as
you have Python 2.6, 2.7 or 3, fcache should run just fine.

Pip
~~~

To keep things simple, install fcache using
`pip <http://www.pip-installer.org/>`_:

.. code:: bash

    $ pip install fcache

This will download fcache from
`the Python Package Index <http://pypi.python.org/>`_ and install it in your
Python's ``site-packages`` directory.

Tarball Release
~~~~~~~~~~~~~~~

If you'd rather install fcache manually:

1.  Download the most recent release from `fcache's PyPi page <http://pypi.python.org/pypi/fcache/>`_.
2. Unpack the tarball.
3. From inside the directory ``fcache-XX``, run ``python setup.py install``

This will install fcache in your Python's ``site-packages`` directory.

Install the Development Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`fcache's code <https://github.com/tsroten/fcache>`_ is hosted at GitHub.
To install the development version first make sure `Git <http://git-scm.org/>`_
is installed. Then run:

.. code-block:: bash
   
    $ git clone git://github.com/tsroten/fcache.git
    $ pip install -e fcache

This will link the ``fcache`` directory into your ``site-packages``
directory.

Running the Tests
~~~~~~~~~~~~~~~~~

Running the tests is easy:

.. code-block:: bash

    $ python setup.py test

If you want to run the tests using different versions of Python, install and
run tox:

.. code-block:: bash

    $ pip install tox
    $ tox

Getting Started
---------------

Let's create a file cache:

.. code:: python

    >>> from fcache.cache import FileCache
    >>> mycache = FileCache('cache_dir')

You can use the cache just like a :class:`dict`:

.. code:: python

    >>> mycache['foo'] = 'value'
    >>> mycache['foo']
    'value'
    >>> mycache['bar'] = 'blah'
    >>> list(mycache)
    ['foo', 'bar']
    >>> del mycache['bar']

By default, the cache object stores changes in a buffer that needs to be
explicitly synced with the cache's files:

.. code:: python

    >>> mycache.sync()
    >>> # closing a cache also syncs it:
    ... mycache.close()

If you want the cache to automatically write changes to disk everytime you
add/modify values, open the cache and append ``'s'`` to the optional *flag*
argument:

.. code:: python

    >>> mycache = FileCache('cache_dir', flag='cs')

The ``'c'`` means that the object will open a cache if it exists, but will
create a new one if no cache is found. The ``'s'`` means that the cache is
opened in sync mode. All changes are immediately written to disk.

Using fcache with a :class:`~shelve.Shelf`
------------------------------------------

Python's :class:`~shelve.Shelf` class provides a persistent dictionary-like
object. Shelves normally use the :mod:`dbm` module as a backend. You can use easily use
fcache as a shelf's backend if needed. Because shelves already serialize data,
you'll need to tell fcache not to serialize the data:

.. code:: python

    >>> mycache = FileCache('cache_dir', serialize=False)
    >>> myshelf = Shelf(mycache)

That's it! You can use the :class:`~shelve.Shelf` just like you normally
would.

API
---

.. automodule:: fcache.cache

.. autoclass:: FileCache

    .. automethod:: close
    .. automethod:: create
    .. automethod:: delete
    .. automethod:: sync

    In addition to the four methods listed above, :class:`FileCache` objects
    also support the following standard :class:`dict` operations and methods:

    .. describe:: len(f)

        Return the number of items in the :class:`FileCache` *f*.

    .. describe:: f[key]

        Return the item of *f* with key *key*. Raises a :exc:`KeyError` if *key*
        is not in the cache.

    .. describe:: f[key] = value

        Set ``f[key]`` to *value*.

    .. describe:: del f[key]

        Remove ``f[key]`` from *f*.  Raises a :exc:`KeyError` if *key* is not in the
        cache.

    .. describe:: key in f

        Return ``True`` if *f* has a key *key*, else ``False``.

    .. describe:: key not in f

        Equivalent to ``not key in f``.

    .. describe:: iter(f)

        Return an iterator over the keys of the cache.  This is a shortcut
        for ``iter(f.keys())`` (``iterkeys()`` in Python 2).

    .. automethod:: clear()
        
    .. method:: get(key[, default])

        Return the value for *key* if *key* is in the cache, else *default*.
        If *default* is not given, it defaults to ``None``, so that this method
        never raises a :exc:`KeyError`.

    .. method:: items()

        Return a new view of the cache's items (``(key, value)`` pairs).
        See the :ref:`documentation of view objects <dict-views>`.

        In Python 2, this method returns a copy of the cache's list of
        ``(key, value)`` pairs.

    .. method:: keys()

        Return a new view of the cache's keys.  See the :ref:`documentation
        of view objects <dict-views>`.

        In Python 2, this method returns a copy of the cache's list of keys.

    .. method:: pop(key[, default])

        If *key* is in the cache, remove it and return its value, else return
        *default*.  If *default* is not given and *key* is not in the cache,
        a :exc:`KeyError` is raised.

    .. method:: popitem()

        Remove and return an arbitrary ``(key, value)`` pair from the cache.

    .. method:: setdefault(key[, default])

        If *key* is in the cache, return its value.  If not, insert *key*
        with a value of *default* and return *default*.  *default* defaults to
        ``None``.

    .. method:: update([other])

        Update the cache with the key/value pairs from *other*, overwriting
        existing keys.  Return ``None``.

    .. method:: values()

        Return a new view of the cache's values.  See the
        :ref:`documentation of view objects <dict-views>`.

        In Python 2, this method returns a copy of the cache's list of values.

.. include:: ../CHANGES.txt
