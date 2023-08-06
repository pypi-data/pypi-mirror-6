.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 12:22:06 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _tourney management:

Tourney management
==================

.. figure:: tourney.png

   Tourney management

This is the core window of the application and is composed by four *panels*. On the left
there's the `competitors`_ one, where you can subscribe new players, retire existing ones or
rearrange them in teams if season's :guilabel:`players per team` is bigger than 1 (first turn
only). On the right there's the `ranking`_ panel, where you can see the current ranking,
possibly grouped by nationality. At the bottom there's the `first turn`_ view that let you
alter the random combination generated for the first turn. The remaining space in the middle is
dedicated to the `matches`_.

The three panels on the borders can be minimized, thus maximizing the space for the
matches_. In particular, the one on the left and the one at the bottom are mainly used only
just before and just after the first turn is created.

.. note:: General and federal rankings are basically summaries of a set of tourneys. Since they
          are computed using the **final prize** of each competitor (possibly multiplied by the
          tourney's *prize factor*), obviously **only** *prized* tourneys are taken into
          account.

          This also means that if a tourney is being inserted "after the fact", just to
          introduce its scoring into the general rankings, details about single rounds may be
          omitted. In this case follow these steps:

          1. insert the list of competitors
          2. confirm the changes
          3. assign final prizes, with the :guilabel:`prize` button in the ranking_ panel: this
             will show the :guilabel:`final prize` column
          4. manually change each competitor's final prize, accordingly to the effective
             tourney's ranking
          5. confirm the changes

.. _competitors panel:

.. figure:: competitors_1.png
   :figclass: float-right

   Competitors panel

Competitors
-----------

This panel is used mainly at the start of a new tourney, to compose the group of participating
players. Using *drag&drop* you can either insert new players or rearrange them in teams, as
shown in the figure: you can drag single players from one team to another, or add new players
picking them from the :ref:`players <players management>` window. The :guilabel:`add...` button
brings up that window, showing only players **not yet** associated with the tourney.

.. note:: It is possible to add new players at any time, even when the tournament has already
          started and some matches has been played: even if this is not allowed in official
          tourneys, in amateur events it may happen that a player is late, or that one person
          of the public asks to enter the game. In such case, the new player gets zero points
          and is positioned at the end of the current ranking.

.. figure:: competitors_2.png
   :figclass: float-left

   Adjusted teams

You can see that there is a new completed team (with a green background); one team is not
complete because it has only one player: this has no effect on the succeding operations (it can
be played without problems) although it would be quite strange; another team will be deleted
(red background) because it's only player has been removed.

.. hint:: Players may be removed from the panel by dragging them and dropping over any empty
          space (the scrollbar, when the panel is full): the icon associated to the drag
          operation will reflect the case.

.. important:: It's not possible to change the composition of a team once the first round has
               been played, for obvious reasons.

.. figure:: retire.png
   :figclass: float-right

   Retire confirmation

A competitor may be retired by double-clicking it and confirming the action: this means that he
won't participate to further games. He will show up in the ranking, though.

.. topic:: Teams

   From the application point of view, the number of players that compose a single competitor
   does **not** make any difference. Each game involves *two* distinct *competitors*, no matter
   how many players are grouped in each one, each group represent a *single* entity.

   When organizing a teamed championship, beware that any team is determined by the people
   assigned to it **and** by their ordering: the team `John and Paul` is **different** from the
   one composed by `Paul and John`, that is the same guys but in different order! This is where
   the `duplicate tourney` action is very useful.

   .. note:: The :guilabel:`nationality` of a team is determined by that of its first player,
             so order *matters*: be sure to drag in players in the right sequence.


First turn
----------

Once the subscription has been completed, the next step is to generate the first round of the
tournament, that will be done taking into account the current rate of each player if the
tourney is linked to a particular :ref:`rating <glicko rating management>`, otherwise by
coupling randomly the competitors.

.. figure:: firstturn.png

   First turn recombination

The `arbiter` may decide that the random combination generated by the application for the first
turn is not adeguate and some manual intervention is required. In this window, enabled **only**
before the first turn is actually played, you can drag&drop competitors around, swapping them
as desired.

Even the association of matches with the carrom boards is random, for the first round. From the
second on ``SoL`` tries to give a different board for each turn to a given player, following
ranking order. This guarantees that top players will preferably play on different low-numbered
boards, while weaker ones will use high-numbered boards, possibly repeatedly, in particular
when the number of players (and thus the number of tables) is very low.


.. figure:: deleteturn.png
   :figclass: float-right

   Deletion of turns

Matches
-------

The middle panel is where most of the activity happens: here you iteratively create next turn,
insert its results and compute the new ranking.

Of course, only the **last** turn is editable, that is, you cannot alter previous rounds
results. If something went wrong and you need to rectify any previous score, you must *delete*
the last turn (or even more than one, should that make any sense at all), make the change and
regenerate the new turn.

.. hint:: To insert the results of each round you may follow two distinct strategies:

          a. order the scorecards by board number and the insert the scores of each one: in
             this case you can use the :kbd:`TAB` key that moves the *focus* to the next field;

          b. when you have many boards (and thus the manual sort would be very tedious), you
             can “jump” directly to the result of a particular board by simply entering the
             board number: the *focus* will be moved to the right row and the score of the
             first competitor will be activated for editing.

.. figure:: rankingbynation.png
   :figclass: float-right

   Ranking grouped by nationality

Ranking
-------

Whenever you change and commit the results of the last round the ranking is automatically
recomputed and shown here. The :guilabel:`prize` column is usually hidden until *prize giving*.

.. You can see the *national ranking*, grouping the view by the nationality of the
   competitor. The :guilabel:`print` button takes the current view in account and thus it emits
   the normal or the grouped printout.

.. hint:: By double-clicking on a competitor the matches_ panel focuses on him showing only his
          matches. You can see any other player details by double-clicking on another name. The
          match panel returns to the usual view either by double-clicking the same player a
          second time, or when a new turn is created.

Once the :guilabel:`Prize-giving` is done, the :guilabel:`prize` column becomes editable,
either to manually force the prizes, or to eventually swap top players after the final.
