nextversion
~~~~~~~~~~~
.. image:: https://travis-ci.org/laysakura/nextversion.png?branch=master
   :target: https://travis-ci.org/laysakura/nextversion

.. image:: https://pypip.in/v/nextversion/badge.png
    :target: https://pypi.python.org/pypi/nextversion
    :alt: Latest PyPI version

A Python package to increments module verision numbers.

.. code-block:: python

    from nextversion import nextversion
    nextversion('1.0a2')    # => '1.0a3'
    nextversion('v1.0a2')   # => '1.0a3'  (normalized to compatible version with PEP 386)
    nextversion('foo.0.3')  # => None     (impossible to normalize)

If original version number does not match `PEP 386 <http://www.python.org/dev/peps/pep-0386/>`_ ,

1. Next version compatible with `PEP 386 <http://www.python.org/dev/peps/pep-0386/>`_ is returned if possible,
2. If impossible, `None` is returned.

Install
=======

Install from PyPI
-----------------

.. code-block:: bash

    $ pip install nextversion

Install from Github repo
------------------------

.. code-block:: bash

    $ git clone https://github.com/laysakura/nextversion.git
    $ cd nextversion
    $ ./setup.py install


See also
========

- `PEP 386 <http://www.python.org/dev/peps/pep-0386/>`_
- `Version::Next <http://search.cpan.org/perldoc?Version::Next>`_ CPAN module

Author
======

Sho Nakatani <lay.sakura@gmail.com>, a.k.a. @laysakura
