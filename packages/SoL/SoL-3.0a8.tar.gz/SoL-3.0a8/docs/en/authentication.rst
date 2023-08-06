.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 12:25:33 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _authentication:

.. figure:: authentication.png
   :figclass: float-right

   The authentication panel


Authentication
==============

First of all, you must authenticate yourself.

.. rubric::  *Hey, what the heck... ⁉⁈*

SoL is a `client/server` application, that is, there are two
components. On one side there is the *client*, an application running
within any modern graphical web browser such as Firefox__; this
application talks with a *server*, the other side, that effectively
manages the database, and implements the so called `business logic`__.

The two components talks to each other thru a *connection*, that can
be either a **local** one, where both side actually run on a
**single** machine, as two different programs that run in parallel, or
a **network** connection, where there are **two** (or more) computers
involved, either on a `LAN`__ or even thru Internet.

This allows three scenarios:

1. the most simple one, a single standalone machine without any
   network capability, possibly with a printer: everything is done on
   this single station;

2. a set of computers connected thru a ``LAN``, one of which is the
   server, where one or more clients connect to it: imagine you are
   organizing the European Championship, and there are pressmen who'd
   like to see the ranking directly on their laptop, possibly using
   the local wireless network...

3. the server is on the Internet, accessible from the outside: this
   may be just for showing your club's championship, or even to supply
   it as a on-line public service, where other people can organize
   their own.

So, back to the question: yes, it may be a little annoying to enter
your credentials, but it's an honest price to pay for these
capabilities.

Any registered player may be allowed to login, simply assigning him a
`nickname` and a `password`.

__ http://en.wikipedia.org/wiki/Business_logic
__ http://en.wikipedia.org/wiki/Local_area_network
__ http://www.mozilla.org/en-US/firefox/new
