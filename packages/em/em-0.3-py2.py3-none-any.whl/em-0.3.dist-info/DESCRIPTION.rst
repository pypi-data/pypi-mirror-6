Em
--

Em is a terminal tool that prints FILE(s), or standard input to standard
output and highlights the expressions that are matched the PATTERN.

The expression will be highlighted iff the terminal is ANSI-compatible.


Em is Cool
``````````

.. code:: bash

    $ tail -f /path/to/log | em "DEBUG|INFO" GREEN | em "WARN" yellow


Links
`````

* `documentation <http://em.readthedocs.org/>`_
* `source code <https://github.com/ikalnitsky/em>`_



