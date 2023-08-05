====
ralc
====

.. image:: https://travis-ci.org/playpauseandstop/ralc.png?branch=master
    :target: https://travis-ci.org/playpauseandstop/ralc

.. image:: https://pypip.in/v/ralc/badge.png
    :target: https://pypi.python.org/pypi/ralc

Rate Calculator for multiplicate spent hours with rate per hour to find out how
many money you earned.

Requirements
============

* `Python <http://www.python.org/>`_ 2.6+

Installation
============

As easy as::

    # pip install ralc

License
=======

``ralc`` is licensed under the terms of `BSD License
<https://github.com/playpauseandstop/ralc/blob/master/LICENSE>`_

Usage
=====

::

    usage: ralc [-h] HH[:MM[:SS]] RATE

    Rate Calculator

    positional arguments:
      HH[:MM[:SS]]  Spent hours, e.g.: "30", "120:40", "10:55:30"
      RATE          Rate per hour. Should be decimal value.

    optional arguments:
      -h, --help    show this help message and exit

Changelog
=========

0.1 (2014-01-16)
----------------

+ Initial release
