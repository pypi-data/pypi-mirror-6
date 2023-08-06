.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    sab 08 nov 2008 20:45:42 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

==============================================
 :mod:`sol.models` -- SQLAlchemy modelization
==============================================

.. automodule:: sol.models

.. autoclass:: sol.models.AbstractBase
   :members:

.. autoclass:: sol.models.GloballyUnique
   :members:


Entities
========

.. toctree::
   :maxdepth: 2

   clubs
   championships
   competitors
   matches
   mergedplayers
   players
   tourneys
   ratings
   rates



Batched I/O
===========

.. automodule:: sol.models.bio

.. autofunction:: save_changes

.. autofunction:: backup
.. autofunction:: restore

.. autofunction:: load_sol
.. autofunction:: dump_sol

.. autoclass:: Serializer
.. autoclass:: Deserializer


Utilities
=========

.. automodule:: sol.models.utils

.. autofunction:: asunicode
.. autofunction:: normalize
.. autofunction:: njoin
.. autofunction:: entity_from_primary_key
.. autofunction:: table_from_primary_key
