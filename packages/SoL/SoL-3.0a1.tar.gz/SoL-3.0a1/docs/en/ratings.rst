.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    dom 29 dic 2013 10:47:26 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _glicko rating:

.. index::
   pair: ratings; glicko

Glicko ratings
--------------

Version 3 of SoL introduced a management of players ratings following the
`Glicko system`__, mainly to get rid of the *random* component when
generating the first turn couplings in *important* tourneys.

__ http://en.wikipedia.org/wiki/Glicko_rating_system

When a tourney is associated to a particular *Glicko rating*, the turn
generation algorithm takes into account the *current rate* of each
player.
