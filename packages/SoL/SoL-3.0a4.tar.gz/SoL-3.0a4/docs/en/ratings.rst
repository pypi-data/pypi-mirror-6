.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    dom 29 dic 2013 10:47:26 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _glicko rating management:

Glicko ratings
--------------

.. index::
   pair: ratings; glicko

Version 3 of SoL introduced a management of players ratings following the `Glicko system`__,
mainly to get rid of the *random* component when generating the first turn couplings in
*important* tourneys.

To put it simply, the system computes a rate of each player that represent the mutual
probability of victory: a player rated 2200 will most probably win a match against a player
rated 1700.

__ http://en.wikipedia.org/wiki/Glicko_rating_system

When a tourney is associated to a particular *Glicko rating*, the turn generation algorithm
takes into account the *current rate* of each player.


Menu actions
~~~~~~~~~~~~

In addition to the :ref:`standard actions <standard actions>` the menu at the top contains the
following items:

:guilabel:`Tourneys`
  Opens the :ref:`management of the tourneys <tourneys management>`
  associated with the selected rating

:guilabel:`Players`
  Opens the :ref:`rates of the players <players rates>` of the selected rating

:guilabel:`Recompute`
  Recompute the whole rating, elaborating all the results of all the tourneys associated with
  the selected rating

:guilabel:`Download`
  Download an archive of all the tourneys associated with the selected rating


Insert and edit
~~~~~~~~~~~~~~~

.. index::
   pair: Insert and edit; Rating

Each rating has a :guilabel:`description` that must be unique, i.e. it is not possible to
insert two distinct ratings with the same description.

The :guilabel:`level` represent the *importance* of the rating and its *dependability*. The
rate of a player playing in a tourney associated with a particular rating is his most recent
rate in the referenced rating **or** one with the *same* level or *greater*.

The :guilabel:`tau` is the primary coefficient that drives the computation in the Glicko2
algorithm.

The :guilabel:`rate`, the :guilabel:`deviation` and the :guilabel:`volatility` are the default
values of the rate of a player at his first tourney with the given rating.

.. important:: Only the system administrator is allowed to change these values: usually they
               should not be modified.

               In any case, when these values get changed the rating should be recomputed.
