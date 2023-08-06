==========
ISBN tools
==========

Info
====

``isbntools`` provides several useful methods and functions
to validate, clean and transform ISBN strings.

Typical usage (as library):

.. code-block:: python

    #!/usr/bin/env python
    import isbntools
    ...

Several scripts are provided to use from the command line:

.. code-block:: bash

    $ to_isbn10 ISBN13

transforms an ISBN10 number to ISBN13.

.. code-block:: bash

    $ to_isbn13 ISBN10

transforms an ISBN13 number to ISBN10.

.. code-block:: bash

    $ isbn_info ISBN

gives you the *group identifier* of the ISBN.

.. code-block:: bash

    $ isbn_mask ISBN

*masks* (hyphenate) an ISBN (split it by identifiers).

.. code-block:: bash

    $ isbn_meta ISBN

gives you the main metadata associated with the ISBN (uses wcat.org).

.. code-block:: bash

    $ isbn_validate ISBN

validates ISBN10 and ISBN13.

.. code-block:: bash

    $ isbn_stdin_validate

to use with *posix pipes* (e.g. ``cat ISBNs | isbn_stdin_validate``).

.. code-block:: bash

    $ isbntools

writes version and copyright notice.

*Many more scripts could be written with the library*,
using the methods for extraction, cleaning, validation and standardization of ISBNs.


Install
=======

From a command line enter:

.. code-block:: bash

    $ pip install isbntools

or:

.. code-block:: bash

    $ easy_install isbntools

or:

.. code-block:: bash

    $ pip install isbntools-0.7.4.tar.gz


Known Issues
============

1. The ``meta`` method and the ``isbn_meta`` script sometimes give a wrong result
   (this is due to errors on the wcat.org service)


ISBN
====

To know about ISBN:

*  http://en.wikipedia.org/wiki/International_Standard_Book_Number

*  http://www.isbn-international.org/

