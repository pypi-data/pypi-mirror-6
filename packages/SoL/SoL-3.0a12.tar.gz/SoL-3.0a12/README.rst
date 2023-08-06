.. -*- coding: utf-8 -*-

======================
 Scarry On Lin{e|ux}³
======================

-------------------------------------------------------------
Powerful and complete solution to manage Carrom championships
-------------------------------------------------------------

This project contains some tools that make it easier the organization of a championship of
Carrom_.

The main component is a Pyramid_ application serving two distinct user interfaces:

1. A very light, HTML only, read only view of the whole database, where you can actually browse
   thru the tourneys, seasons and players. You can see it in action on the public SoL instance
   at http://sol.metapensiero.it/lit/.

2. A complete ExtJS_ based desktop-like application, that expose all the functionalities
   described below__ in an easy to manage interface, that you can try out visiting
   http://sol.metapensiero.it/.

.. attention:: SoL 3 **requires** Python 3.3 or higher, it does **not** work with Python 2

__ Goals_

.. _Carrom: http://en.wikipedia.org/wiki/Carrom
.. _Pyramid: http://http://www.pylonsproject.org/
.. _ExtJS: http://www.sencha.com/products/extjs/

.. contents::

Goals
=====

These are the key points:

1. Multilingual application

   Scarry spoke only italian, because the i18n mechanism in Delphi (and in general under
   Windows) sucks. Most of the code was written and commented in italian too, and that makes it
   very difficult to get foreign contributions

2. Real database

   Scarry used Paradox tables, but we are in the third millenium, now: SoL uses a real, even if
   simple and light, SQL database under its skin

3. Easy to use

   The application is usually driven by computer-illiterated guys, so little to no surprises

4. Easy to deploy

   Gods know how many hours went in building f*cking installers with BDE goodies

5. Bring back the fun

   Programming in Python is just that, since the beginning


High level description
----------------------

The application implements the following features:

* basic tables editing, like adding a new player, opening a new season, manually tweaking the
  scores, and so on;

* handle a single tourney

  a. compose a list of `competitors`: usually this is just a single player, but there are two
     people in doubles, or more (teams)

  b. set up the first turn, made up of `matches`, each coupling two distinct `competitors`:
     this is usually done randomly, but the arbiter must be able to manually change the
     combinations

  c. print the game sheets, where the player will write the scores

  d. possibly show a clock, to alert the end of the game

  e. insert the score of each table

  f. compute the ranking

  g. print the current ranking

  h. possibly offer a way to retire some competitors, or to add a new competitor

  i. compute the next turn

  j. repeat steps c. thru i. usually up to seven turns

  k. possibly offer a way to go back, delete last turn, correct a score and repeat

  l. recompute the ranking, assigning prizes

* handle a season of tourneys

  * each tourney is associated to one season

  * print the season championship

* data exchange, to import/export whole tourneys in a portable way


Installation and Setup
======================

The very first requirement to install an instance of SoL on your own machine is getting Python
3.3\ [#]_. This step obviously depends on the operating system you are using: on most GNU/Linux
distributions it is already available\ [#]_, for example on Debian and derivatives like Ubuntu
the following command will do the task::

  $ apt-get install python3.3

If instead you are using M$-Windows, you should select the right installer from the downloads__
page on http://www.python.org/. Most probably you need to install also the `Visual Studio 2010
Express`__, or alternatively just its runtime__.

To be able to produce readable PDF you need to install also the `DejaVu fonts`__. As usual, on
GNU/Linux it's a matter of executing the following command::

  $ apt-get install fonts-dejavu

or equivalent for your distribution, while on M$-Windows you need to download__ them and
extract the archive in the right location which usually is ``C:\Windows\Fonts``.

__ http://www.python.org/downloads/windows/
__ http://www.visualstudio.com/downloads/download-visual-studio-vs#d-2010-express
__ http://www.microsoft.com/en-us/download/details.aspx?id=5555
__ http://dejavu-fonts.org/wiki/Main_Page
__ http://sourceforge.net/projects/dejavu/files/dejavu/2.34/dejavu-fonts-ttf-2.34.zip


Easiest way, SoLista
--------------------

The easiest way is using SoLista_, a buildout_ configuration that will perform most of the
needed steps with a few clicks: this is particularly indicated if you are *not* fluent with the
command line interface of your operating system.

Follow the hopefully clear enough steps in SoLista's `README`__.

.. _SoLista: https://bitbucket.org/lele/solista/
.. _buildout: http://www.buildout.org/en/latest/
__ https://bitbucket.org/lele/solista/src/master/README.rst


The manual way
--------------

1. Install ``SoL`` using ``pip``::

    pip install SoL

   that will download the latest version of SoL from PyPI__ and all its dependencies as well

   __ https://pypi.python.org/pypi/SoL

2. Install ExtJS_ 4.2.1::

    python3.3 -m metapensiero.extjs.desktop

3. Create a standard config file::

    soladmin create-config config.ini

   and edit it as appropriate

4. Setup the database::

    soladmin initialize-db config.ini

5. Load official data::

    soladmin restore config.ini

6. Run the application server::

    pserve config.ini

7. Enjoy!
   ::

    firefox http://localhost:6996/

   or, for poor Window$ users or just because using Python makes you
   happier::

    python -m webbrowser http://localhost:6996/


Development
===========

The complete sources are available on Bitbucket__ and can be downloaded with the following
command::

    git clone https://bitbucket.org/lele/sol

After that, you can setup a development environment by executing the command::

    pip install -r requirements/development.txt

If you are a developer, you are encouraged to create your own `fork` of the software and
possibly open a `pull request`: I will happily merge your changes!

You can run the test suite with::

    python3.3 setup.py nosetests

__ https://bitbucket.org/lele/sol


I18N / L10N
-----------

Currently SoL is translated in english and italian. If you know other languages and want to
contribute, the easiest way to create a new translation is to create an account on the
Weblate__ site and follow its `translators guide`__.

__ https://hosted.weblate.org/projects/sol/
__ http://docs.weblate.org/en/latest/user/index.html


Feedback and support
--------------------

If you run in troubles, or want to suggest something, or simply a desire of saying *“Thank
you”* raises up, feel free to contact me via email as ``lele at metapensiero dot it``.

-----

.. [#] As of this writing I'm using version 3.3.5, but SoL should work with the recently
       released Python 3.4 just as well.

.. [#] In fact it may even be already installed!
