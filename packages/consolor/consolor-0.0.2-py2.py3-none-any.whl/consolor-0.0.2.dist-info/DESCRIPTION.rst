consolor
========

.. image:: https://travis-ci.org/paetzke/consolor.png?branch=master
  :target: https://travis-ci.org/paetzke/consolor

Copyright (c) 2013, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

Consolor provides highlighting functions for terminals.

It comes with there 3 functions:

get_line
    Returns a string with the given formatting.

print_line
    Prints a string with the given formatting.

update_line
    Overwrites the output of the current line and prints s on the same line without a new line.

All these functions accept the following formatting parameters:

* *bold*: bool, default False
* *underline*: bool, default False
* *blinking*: bool, default False
* *color*: str, default None
* *bgcolor*: str, default None

Some examples:

.. code:: python

    import consolor

    consolor.print_line('light green', color=consolor.Color.LightGreen)
    consolor.print_line('underline', underline=True)
    consolor.print_line('green bg', bgcolor=consolor.BgColor.Green)
    consolor.update_line('0%')
    consolor.update_line('100%')
    print()

For more colors and background colors see *consolor.Color* and *consolor.BgColor*.

To install ``consolor`` use pip.

.. code:: python

    pip install consolor

Links
-----

* `http://ascii-table.com/ansi-escape-sequences-vt-100.php <http://ascii-table.com/ansi-escape-sequences-vt-100.php>`_
* `http://wiki.ubuntuusers.de/Bash/Prompt <http://wiki.ubuntuusers.de/Bash/Prompt>`_


