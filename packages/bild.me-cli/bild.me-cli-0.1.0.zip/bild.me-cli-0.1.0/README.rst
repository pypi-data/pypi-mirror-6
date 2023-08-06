bild.me-cli
============

CLI tool for bild.me.

|Build|


* GitHub: https://github.com/mozillazg/bild.me-cli
* Free software: MIT license
* PyPI: https://pypi.python.org/pypi/bild.me-cli
* Python version: 2.6, 2.7, pypy, 3.3


Installation
------------

To install bild.me-cli, simply:

.. code-block:: bash

    $ pip install bild.me-cli


Usage
------

.. code-block:: console

    $ bild -f test1.png test2.png
    http://s1.bild.me/bilder/260513/3599206test2.png
    http://s1.bild.me/bilder/260513/8204314test1.png
    
    $ bild -h
    usage: bild-script.py [-h] [-V] [-l] -f FILE [FILE ...]

    CLI tool for bild.me.

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      -l, --list            list all result
      -f FILE [FILE ...], -F FILE [FILE ...], --file FILE [FILE ...]
                            picture file


.. |Build| image:: https://api.travis-ci.org/mozillazg/bild.me-cli.png?branch=master
   :target: https://travis-ci.org/mozillazg/bild.me-cli
