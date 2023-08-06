Changes
-------

3.0a7 (2014-03-17)
~~~~~~~~~~~~~~~~~~

* Automatic check of the release date in CHANGES.rst

* Fix compatibility with Python 3.4 using Chameleon 2.15

* Fix another glitch when the guest user is not defined in the configuration


3.0a6 (2014-03-08)
~~~~~~~~~~~~~~~~~~

* Add a link to this section (on PyPI) to the login panel


3.0a5 (2014-03-06)
~~~~~~~~~~~~~~~~~~

* New command to update an existing configuration file


3.0a4 (2014-03-06)
~~~~~~~~~~~~~~~~~~

* Fix minor deploy issue with metapensiero.extjs.desktop


3.0a3 (2014-03-06)
~~~~~~~~~~~~~~~~~~

* Tweak the deployment infrastructure

* Change package description to improve the chance it gets found

* Some work on the user manuals


3.0a2 (2014-03-04)
~~~~~~~~~~~~~~~~~~

* Fix various deploy related issues


3.0a1 (2014-03-03)
~~~~~~~~~~~~~~~~~~

* Let's try the release process!


Version 3
~~~~~~~~~

* Ported to Python 3.3 and to ExtJS 4.2

* Built on `metapensiero.extjs.desktop`__ and `metapensiero.sqlalchemy.proxy`__

  __ https://pypi.python.org/pypi/metapensiero.extjs.desktop
  __ https://pypi.python.org/pypi/metapensiero.sqlalchemy.proxy

* Version control moved from darcs__ to git__ (darcs is beautiful, but git is more powerful and
  many more people use it)

  __ http://darcs.net/
  __ http://git-scm.com/

* It tooks almost one year and more than 760 changesets (still counting!)...


Highlights
++++++++++

* Glicko2__ ratings, with graphical charts

  __ http://en.wikipedia.org/wiki/Glicko_rating_system

* Old `championships` are gone, old `seasons` has been renamed to `championships`

  People got confused by the overlapping functionality, old championships were an attempt to
  compute national-wide rankings: the new Glicko2-based ratings are much better at that

* Augmented players information to fit international tourneys requirements, clubs may be marked
  as `federations`

* Easier interfaces to insert and modify

* Easier way to upload players portraits and clubs logos

* Hopefully easier installation

* Better infrastructure to accomodate database migrations

* Simpler way to detect potential duplicated players

* Most entities carry a ``GUID`` that make it possible to reliably match them when imported
  from a different SoL instance

* Players merges are tracked and distribuited to other SoL instances


Dark ages
~~~~~~~~~

``Scarry`` was a `Delphi 5`__ application I wrote years ago, with the equivalent goal. It
started as a "quick and dirty" solution to the problem, and Delphi was quite good at that. It
has served us with good enough reliability for years, but since programming in that environment
really boring nowadays, there's no way I could be convinced to enhance it further.

``SoL`` is a complete reimplementation, restarting from scratch: it uses exclusively `free
software`__ components, so that I won't be embaraced to public the whole source code.

__ http://en.wikipedia.org/wiki/Borland_Delphi
__ http://en.wikipedia.org/wiki/Free_software
