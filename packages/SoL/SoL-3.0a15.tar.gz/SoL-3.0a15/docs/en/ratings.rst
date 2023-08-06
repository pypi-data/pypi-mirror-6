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

The :guilabel:`level` represent the *importance* of the rating and its *dependability*.

If :guilabel:`inherit` is active, then the rate of a player playing in a tourney associated
with a particular rating is his most recent rate in the referenced rating **or** one with the
*same* level or *greater*. When it is not active, the search is limited exclusively to the
referenced rating.

The :guilabel:`tau` is the primary coefficient that drives the computation in the Glicko2
algorithm.

The :guilabel:`rate`, the :guilabel:`deviation` and the :guilabel:`volatility` are the default
values of the rate of a player at his first tourney with the given rating.

.. important:: Only the system administrator is allowed to change these values: usually they
               should not be modified.

               In any case, when these values get changed the rating should be recomputed.


Historical ratings
~~~~~~~~~~~~~~~~~~

Historical ratings may be loaded with the ``soladmin load-historical-rating`` command line tool
that accepts the following options and requires two positional arguments, respectively the
configuration file and an URL of the file containing the historical ratings:

--date         Bogus rates date, by default 1900-01-01
--deviation    Value of the deviation, by default 100, or a formula to compute it from other
               fields
--volatility   Value of the volatility, by default 0.006, or a formula to compute it from other
               fields
--rate         Formula to compute the player's rate, if the value in the file needs to be
               adjusted
--description  Description of the historical rating
--level        The level of the rating, 0 by default: 0=historical, 1=international,
               2=national, 3=regional, 4=courtyard
--inherit      Whether player's rate will be inherited from other ratings at the same level or
               better, False by default
--map          Specify a map between internal (SoL) field name and external one
--encoding     Encoding of the CSV file, by default UTF-8
--tsv          Fields are separated by a TAB, not by a comma
--dry-run      Just show the result, do not actually insert data

The data file may be specified either as an URL like ``http://hostname.com/path/to/data.txt``
or as a local file with ``file:///tmp/data.txt``.

The specified text file must contain either `comma-separated-values` or `tab-separated-values`
(if the option ``--tsv`` is given) lines. If not otherwise specified with the option
``--encoding`` it is loaded as an UTF-8 stream.

The first row is considered as the `header` that specifies the names of each column and the
remaining rows are considered the real data, each one containing the value of the rate of a
single player.

Any single row must contain at least the fields ``firstname``, ``lastname`` and ``nickname`` to
univocally identify a particular player, and optionally his ``sex`` and the ``club`` he plays
for. There must obviously be the ``rate`` field containing the actual value of his historical
rate. These are the `internal names` of the fields, but with the option ``--map`` you can
specify an arbitrary mapping to the actual names used in the file.

As an example, the following data

::

    id,surname,firstname,nickname,rating,matches_played,club,sex
    1,Gaifas,EMANUELE,,1000,30,,Scarambol Club Rovereto,M
    2,ROSSI,PAOLO,,1468,6,Scarambol Club Rovereto,M
    3,Verdi,Giuseppe,,1427,34,Italian Carrom Federation,M
    4,Bianchi,Stefania,,1495,7,,F

may be loaded with the following command::

    soladmin load-historical-rating \
             --map lastname=surname \
             --map rate=rating \
             --map matches_played=matches_played \
             --map club \
             --map sex \
             --deviation "350.0 / (10.0 - 9.0*exp(-matches_played / 60.0))" \
             --description "Historical rating" \
             --dry-run \
             config.ini /tmp/players.csv

that should produce something like the following output::

    Loading ratings from file:///tmp/players.csv...
    Gaifas Emanuele “lele” (Scarambol Club Rovereto): rate=1000 deviation=77 volatility=0.006
    NEW Rossi Paolo (Scarambol Club Rovereto): rate=1468 deviation=188 volatility=0.006
    NEW Verdi Giuseppe (Italian Carrom Federation): rate=1427 deviation=71 volatility=0.006
    NEW Bianchi Stefania (None): rate=1495 deviation=175 volatility=0.006

where you can see that:

a. the ``--dry-run`` option just shows what would happen, without altering the database
b. player's names are *normalized*, that is "EMANUELE" becomes "Emanuele"
c. new players are automatically added to the database
d. the deviation value is computed from the number of played matches

When you are satisfied, omit the ``--dry-run`` option and the data will be effectively loaded.
