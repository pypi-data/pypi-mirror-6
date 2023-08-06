``print``, ``format``, and ``%``, evolved.

    **Q:** It's been *forty years* since ``C`` introduced ``printf()`` and the basic
    formatted printing of positional parameters. Isn't it time for an upgrade?

    **A:** Yes! ZOMG, yes!

.. image:: https://pypip.in/d/say/badge.png
    :target: https://crate.io/packages/say/

``say`` goes beyond Python's ``print``
statement/function, ``format`` function/method, and ``%`` string interpolation
operator with simpler, higher-level facilities. For example::

    from say import say

    x, nums, name = 12, list(range(4)), 'Fred'

    say("There are {x} things.")
    say("Nums has {len(nums)} items: {nums}")
    say("Name: {name!r}")

yields::

    There are 12 things.
    Nums has 4 items: [0, 1, 2, 3]
    Name: 'Fred'

At this level, ``say`` is basically a simpler, nicer recasting of::

    from __future__ import print_function

    print("There are {0} things.".format(x))
    print("Nums has {0} items: {1}".format(len(nums), nums))
    print("Name: {0!r}".format(name))

The more items being printed, and the more complicated the ``format``
invocation, the more valuable this simple inline specification becomes.

One final example::

    say.title('Discovered')
    say("Name: {name:style=blue}", indent='+1')
    say("Age:  {age:style=blue}", indent='+1')

Prints a nicely formatted text block, with a propert title and indentation,
and just the variable information in blue.

Beyond DRY, Pythonic templates that piggyback the
Python's well-proven ``format()`` method, syntax, and underlying engine,
``say``'s virtues include:

  * A single output mechanism that works the same in either Python 2 or
    Python 3.
  * A companion ``fmt()`` object for string formatting.
  * Higher-order line formatting such as line numbering,
    indentation, and wrapping built in.
  * Convenient methods for common formatting items such as titles, horizontal
    separators, and vertical whitespace.
  * Easy styled output, including ANSI colors and user-defined styles
    and text transforms.
  * Easy output to one or more files, with no additional code.
  * Super-duper template/text aggregator objects for easily building,
    reading, and writing multi-line texts.

Take it for a test drive today! See also `the full documentation
at Read the Docs <http://say.readthedocs.org/en/latest/>`_.
