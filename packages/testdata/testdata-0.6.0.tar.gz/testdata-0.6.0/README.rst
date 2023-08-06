Testdata
========

Generate Random Test Data.

These are just a bunch of functions designed to make it easier to test
your code.

To use testdata in your tests, just include the ``testdata.py`` module:

::

    import testdata

To install, use Pip:

::

    pip install testdata

Or, with Pip using Github:

::

    pip install git+https://github.com/Jaymon/testdata#egg=testdata

Functions
---------

--------------

patch
~~~~~

.. code:: python

    patch(mod, **patches)

Patches a module or class with the given patches.

Suppose you had a module like this:

.. code:: python

    # module foo.bar

    def boom():
        return 1

    class FooPatch(object):
        @classmethod
        def bam(cls): return boom()

Now you can easily patch it for testing:

.. code:: python

    def mock_boom():
        return 2

    foo_bar = testdata.patch('foo.bar', boom=mock_boom)
    print foo_bar.FooPatch.bam() # 2

    # but you can also just pass in objects or modules

    from foo.bar import FooPatch
    FooPatch = testdata.patch(FooPatch, boom=mock_boom)
    print FooPatch.bam() # 2

    from foo import bar
    bar = testdata.patch(bar, boom=mock_boom)
    print bar.FooPatch.bam() # 2

--------------

create\_file\_structure
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    create_file_structure(file_structure, tmpdir=u'')

This just makes it easy to create a lot of folders/files all at once.

.. code:: python

    base_dir = "/tmp"
    tmpdir, created_dirs, created_files = testdata.create_file_structure(
      """
      /foo/
        /bar/
          /che.txt
          /bam.txt
        /baz
          /flam.txt
      """,
      tmpdir=base_dir
    )

--------------

create\_dir
~~~~~~~~~~~

.. code:: python

    create_dir(path, tmpdir=u"")

create a directory hierarchy

.. code:: python

    base_dir = "/tmp"
    d = testdata.create_dir("/foo/bar", base_dir)
    print d # /tmp/foo/bar

--------------

create\_file
~~~~~~~~~~~~

.. code:: python

    create_file(path, contents=u"", tmpdir=u"")

create a file with contents

.. code:: python

    base_dir = "/tmp"
    f = testdata.create_file("/foo/bar.txt", "The file contents", base_dir)
    print f # /tmp/foo/bar.txt

--------------

create\_files
~~~~~~~~~~~~~

.. code:: python

    create_files(file_dict, tmpdir=u"")

Create a whole bunch of files, the ``file_dict`` key is the filename,
the value is the contents of the file. The ``file_dict`` is very similar
to the ``create_modules`` param ``module_dict``

--------------

create\_module
~~~~~~~~~~~~~~

.. code:: python

    create_module(module_name, contents=u"", tmpdir=u"", make_importable=True)

create a module with python contents that can be imported

.. code:: python

    base_dir = "/tmp"
    f = testdata.create_module("foo.bar", "class Che(object): pass", base_dir)
    print f # /tmp/foo/bar.py

--------------

create\_modules
~~~~~~~~~~~~~~~

.. code:: python

    create_modules(module_dict, tmpdir=u"", make_importable=True)

create a whole bunch of modules at once

.. code:: python

    f = testdata.create_modules(
      {
        "foo.bar": "class Che(object): pass",
        "foo.bar.baz": "class Boom(object): pass",
        "foo.che": "class Bam(object): pass",
      }
    )

--------------

get\_ascii
~~~~~~~~~~

.. code:: python

    get_ascii(str_size=0)

return a string of ascii characters

::

    >>> testdata.get_ascii()
    u'IFUKzVAauqgyRY6OV'

--------------

get\_float
~~~~~~~~~~

.. code:: python

    get_float(min_size=None, max_size=None)

return a floating point number between ``min_size`` and ``max_size``.

::

    >>> testdata.get_float()
    2.932229899095845e+307

--------------

get\_int
~~~~~~~~

.. code:: python

    get_int(min_size=1, max_size=sys.maxsize)

return an integer between ``min_size`` and ``max_size``.

::

    >>> testdata.get_int()
    3820706953806377295

--------------

get\_name
~~~~~~~~~

.. code:: python

    get_name(name_count=2, as_str=True)

returns a random name that can be outside the ascii range (eg, name can
be unicode)

::

    >>> testdata.get_name()
    u'jamel clarke-cabrera'

--------------

get\_str
~~~~~~~~

.. code:: python

    get_str(str_size=0, chars=None)

return random characters, which can be unicode.

::

    >>> testdata.get_str()
    u"q\x0bwZ\u79755\ud077\u027aYm\ud0d8JK\x07\U0010df418tx\x16"

--------------

get\_url
~~~~~~~~

.. code:: python

    get_url()

return a random url.

::

    >>> testdata.get_url()
    u'https://sK6rxrCa626TkQddTyf.com'

--------------

get\_words
~~~~~~~~~~

.. code:: python

    get_words(word_count=0, as_str=True)

return a random amount of words, which can be unicode.

::

    >>> testdata.get_words()
    u"\u043f\u043e\u043d\u044f\u0442\u044c \u043c\u043e\u0436\u043d\u043e felis, habitasse ultrices Nam \u0436\u0435\u043d\u0430"

--------------

get\_past\_datetime
~~~~~~~~~~~~~~~~~~~

.. code:: python

    get_past_datetime([now])

return a datetime guaranteed to be in the past from ``now``

::

    >>> testdata.get_past_datetime()
    datetime.datetime(2000, 4, 2, 13, 40, 11, 133351)

--------------

get\_future\_datetime
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    get_future_datetime([now])

return a datetime guaranteed to be in the future from ``now``

::

    >>> testdata.get_future_datetime()
    datetime.datetime(2017, 8, 3, 15, 54, 58, 670249)

--------------

get\_between\_datetime
~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    get_between_datetime(start[, stop])

return a datetime guaranteed to be in the future from ``start`` and in
the past from ``stop``

::

    >>> start = datetime.datetime.utcnow() - datetime.timedelta(days=100)
    >>> testdata.get_between_datetime(start)
    datetime.datetime(2017, 8, 3, 15, 54, 58, 670249)

