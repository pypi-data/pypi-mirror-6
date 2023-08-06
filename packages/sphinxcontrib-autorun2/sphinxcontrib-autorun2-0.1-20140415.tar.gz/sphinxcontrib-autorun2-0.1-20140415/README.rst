=====================
Autorun 
=====================

Autorun2 is an extension for Sphinx_ that can execute the code from a
runblock directive and attach the output of the execution to the document. 

For example::

    .. runblock:: pycon
        
        >>> for i in range(5):
        ...    print i

Produces::

    >>> for i in range(5):
    ...    print i
    1
    2
    3
    4
    5


Autorun2 can also maintain state between invocations::

    Set the variable:

    .. runblock:: pycon

        >>> x = 2

    ... and then print it:

    .. runblock:: pycon

        >>> print x


Produces::

    Set the variable:

    >>> x = 2

    ... and then print it:

    >>> print x
    2

Currently autorun supports ``pycon`` language. It's also possible to configure
autorun (from `conf.py`) to run other languages.


Installation
------------

Installing from PyPI::

    $ pip install sphinxcontrib-autorun 2

Installing from sources::

    $ hg clone http://bitbucket.org/wolever/sphinx-contrib/
    $ cd sphinx-contrib/autorun2
    $ python setup.py install

To enable autorun add 'sphinxcontrib.autorun' to the ``extension`` list in
`conf.py`::

    extensions = [
        'sphinxcontrib.autorun2',
    ]
