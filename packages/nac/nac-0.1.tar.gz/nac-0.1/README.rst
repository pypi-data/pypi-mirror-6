noughts-and-crosses
===================

Simple socket/console game implementation.

dependencies & installation
---------------------------

Works under python version: 2.6, 2.7. No additional dependencies. Install package with pip:

::

    $ pip install nac

overview
--------

This repository holds a python package implementing a simple socket game,
`Noughts and Crosses`_.

.. _Noughts and Crosses: http://en.wikipedia.org/wiki/Tic-tac-toe

First you shall run the server, and then the client:

::

    $ ./nac/server.py
    $ ./nac/client.py

You will see the game board represented by few console lines:

::

    (0)|(1)|(2)
    ---+---+---
    (3)|(4)|(5)
    ---+---+---
    (6)|(7)|(8)

Enter the position you want to put your mark:

Your move: 0

::

     X |(1)|(2)
    ---+---+---
    (3)|(4)|(5)
    ---+---+---
    (6)|(7)|(8)

The server is 'X' and the client is 'O'.

travis
------

This project is continuously integrated with travis-ci.org:

.. image:: https://travis-ci.org/tkoomzaaskz/noughts-and-crosses.png?branch=master
  :target: https://travis-ci.org/tkoomzaaskz/noughts-and-crosses

