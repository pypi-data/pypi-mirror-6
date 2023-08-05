multiplot
---------

Little script to squeeze multiple image files (assumed to be landscape) into
one PDF document.


License
~~~~~~~

To the extent possible under law, Thomas Gläßle has waived all copyright
and related or neighboring rights to multiplot. This work is published
from: Germany.

To the extent possible under law, the person who associated CC0 with
multiplot has waived all copyright and related or neighboring rights
to multiplot.

You should have received a copy of the CC0 legalcode along with this
work. If not, see http://creativecommons.org/publicdomain/zero/1.0/.


Usage
~~~~~

Command line::

    multiplot.py [-k] [-p <per-page>] [-o <output>] <input> ...
    multiplot.py (-h | --help | -v | --version)

Options::

    -k --keep       Keep temporary files
    -p <count>      Set number of images per page
    -o <output>     Set output file name (default is 'multi.pdf')
    -h --help       Show this help
    -v --version    Show version number

Installation
~~~~~~~~~~~~

Either

.. code-block:: bash

    python setup.py install

or just drop the ``multiplot.py`` file into some folder where it can be executed.


Example
~~~~~~~

.. code-block:: bash

    printf '%s\n' graph/*.pdf | sort -V | xargs multiplot -p4

