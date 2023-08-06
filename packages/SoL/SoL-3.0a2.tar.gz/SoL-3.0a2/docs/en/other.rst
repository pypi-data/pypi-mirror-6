.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 12:22:28 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

Other windows
=============

.. _clock:

.. figure:: clock.png
   :figclass: float-right

   The alarm clock window.

Clock
-----

This simple but nice looking widget is based on CoolClock_ and SoundManager_ and implements an
alarmed clock.

The *countdown* may be started either by double-clicking the clock or with the first button;
alternatively you can use the second button that will start the countdown after 15 seconds, so
you can reach your own table in time.

The widget uses :ref:`tourney <tourneys management>` :guilabel:`duration` and
:guilabel:`prealarm` to draw three circles filled in green, orange and red, representing
respectively the start minute, the prealarm minute and the end minute. If you have a fairly
modern HTML5 browser, or if the Flash_ plugin is properly installed in the browser, it will
play a short sound.

At prealarm time the seconds hand will appear and a different sound is played: this usually
means that players should not begin new games but rather finish the current one and then stop.

One minute before end of game it become noisier, emitting a *tic-tac* every second. Finally,
yet another sound is played when the red point is reached: at this point all still going games
should stop, and the result will be computed by the mere difference between not-yet-pocketed
carrommen on the table, ignoring the `Queen`.

Close the clock window when done, or click on the third button.

.. important:: Any time you double-click on the clock, it **resets** the alarm. While this is
               useful in case of a false start, it is potentially dangerous. It is recommended
               that you have another mean of controlling the turn length as a fallback.

.. _coolclock: http://simonbaird.com/coolclock/
.. _soundmanager: http://schillmania.com/projects/soundmanager2/
.. _flash: http://www.adobe.com/go/getflash


.. _upload:

.. figure:: upload.png
   :figclass: float-right

   The upload window.

Upload
------

This very simple window allows the upload of whole tourneys data, as exported by another
instance of SoL. The new data won't clobber existing information though, only missing fields
will be updated of any existing entity.

Anybody can upload ``.sol`` (or ``.sol.gz``, the compressed version) archives. All
authenticated users but `guest` can upload ``.zip`` files with tourneys data, players emblems
and clubs portraits.

.. topic:: Exporting data

   Tourneys data can be exported with the :guilabel:`download` button on :ref:`tourneys
   <tourneys management>` and :ref:`championships <championships management>` windows: they are
   (possibly compressed) simple text files, in YAML__ format, which may be reloaded on another
   SoL instance or archived for security purposes. The archive created in this way contains all
   the specified tourneys as well as the data pertaining to all involved players, clubs and
   seasons. It does **not** contain neither the emblems nor the portraits pictures.

   There is another way to export the whole database, that is *all* tourneys and *all* players
   (also those who never played) **and all** the referenced images. By visiting the URL::

     http://localhost:6996/bio/backup

   SoL will give you a ``ZIP`` archive containing all the above, that can be uploaded into
   another instance of SoL, effectively copying/updating almost all the information and related
   images stored on the source. This is clearly a much bigger archive that the one created with
   the method above, and should be used only migrating the whole database to a newer version of
   SoL, or when you want copy all the images at once.

__ http://www.yaml.org/
