Changes
-------

3.0a2 (2014-03-04)
~~~~~~~~~~~~~~~~~~

* Fix various deploy related issues


3.0a1 (2014-03-03)
~~~~~~~~~~~~~~~~~~

* Let's try the release process!


Version 3
~~~~~~~~~

* Ported to Python 3.3 and to ExtJS 4.2

* Built on `metapensiero.extjs.desktop`__ and
  `metapensiero.sqlalchemy.proxy`__

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
