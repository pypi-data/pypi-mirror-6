.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:16:02 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _championships management:

Championships management
------------------------

.. index::
   pair: Championships; Management

A *championship* is a set of one or more *tourneys*, organized by the
same *club* with the same `format`: all tourneys of a particular
championship are obligatorily all *singles* **or** all *doubles* and
use the same prize-giving method.


Menu actions
~~~~~~~~~~~~

In addition to the :ref:`standard actions <standard actions>` the menu
at the top contains the following items:

.. figure:: championships.png
   :figclass: float-right

   Championships management

:guilabel:`Tourneys`
  Opens the :ref:`management of the tourneys <tourneys management>`
  organized within the selected championship

:guilabel:`Download`
  Downloads an archive of all the tourneys organized within the selected
  championship

:guilabel:`Ranking`
  Creates a PDF document with the ranking of the selected championship


Insert and edit
~~~~~~~~~~~~~~~

.. index::
   pair: Insert and edit; Championship

Each championship has a :guilabel:`description` that must be unique
within the same club.

:guilabel:`Players per team` determines the maximum number of players
participating as a single :ref:`competitor <competitors panel>`: 1 for
singles, 2 for doubles, up to 4 for teams.

With :guilabel:`skip worst prizes` you specify how many *worst* result
will be ignored in the final sum for each player at the end of the
season. This is usually used to tolerate that a player could not
participate to **all** the tourneys of the championship and yet she
remains competitive.

The :guilabel:`coupling method` is used as the default value when
creating new tourneys within the championship and determines how SoL
will couple the participants at each turn (vedi :ref:`coupling
generation method <couplings>` of the tourney for details).

.. index:: Final prizes

The :guilabel:`prize-giving method` field determine the method used to
assign final prizes. These prizes have two primary scopes:

1. to have uniform, and thus `addable`, tourney results with the goal
   of producing the championship ranking

2. by being essentially freely assignable, it becomes possible to swap
   the position of the first two (or four) players should the final (or
   semifinal) match between the first and the second (and between the
   third and fourth) players say so

One particular case is the value ``Simple tourneys, no special
prizes``, which basically means that the prize-giving will use the
competitor's points as the final prize. This method does not satisfy
the first point above, so it's not a good choice for a championship
ranking. These prizes won't appear in the ranking printout of the
tourney, but **are considered** for its order, and they can be
eventually adjusted after the the finals.

The other four values have the following meanings:

``Fixed prizes``
  assigns 18 points to the winner, 16 to the second, 14 to the third,
  13 to the fourth and so on down to the 16th place;

``Fixed 40 prizes``
  assigns 1000 points to the winner, 900 to the second, 800 to the
  third, 750 to the fourth etc, down to 1 point to the 40th place;

``Classic millesimal prizes``
  assigns 1000 points to the winner and a proportional prize to all
  other players; this is usually preferable when the number of
  competitors is higher than 20 or so;

``Weighted on previous season``
  similar to the millesimal method, but uses the previous season
  ranking to assign a *weight* to the tourney distributing a fraction
  of that.

The field :guilabel:`closed` indicates whether the championship is
complete: no other tourney can be associated with these
championships. The championship lookup combos (for example, when
inserting :ref:`new tourneys <tourneys management>`) show only those
still active.

:guilabel:`Previous championship` is used by the weighted prize-giving
method. It allows the selection of one *closed* championship.
