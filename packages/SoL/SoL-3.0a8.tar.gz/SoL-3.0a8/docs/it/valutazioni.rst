.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    dom 29 dic 2013 10:32:04 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _gestione valutazioni glicko:

Gestione valutazioni Glicko
---------------------------

.. index::
   pair: Gestione; Valutazioni Glicko

Dalla versione 3 di SoL è stata introdotta la gestione delle valutazioni dei giocatori secondo
il `sistema Glicko`__, primariamente per permettere di eliminare la componente *casuale* nella
generazione degli accoppiamenti per il primo turno nei tornei *importanti*.

In poche parole, la valutazione dei giocatori calcolata con questo sistema rappresenta la
probabilità di vittoria reciproca: un giocatore con valutazione 2200 molto probabilmente
vincerà scontrandosi con un giocatore con una valutazione 1700.

__ http://it.wikipedia.org/wiki/Sistema_Glicko

Quando un torneo viene associato a una certa *valutazione Glicko*, la generazione dei turni
viene effettuata tenendo conto della *valutazione corrente* di ciascun giocatore.


Voci del menu
~~~~~~~~~~~~~

Oltre alle :ref:`azioni standard <pulsanti-standard>` il menu contiene
queste voci:

:guilabel:`Tornei`
  Apre la :ref:`gestione dei tornei <gestione tornei>` che utilizzano
  la valutazione selezionata

:guilabel:`Giocatori`
  Apre le :ref:`valutazioni dei giocatori <valutazioni giocatori>` secondo
  la valutazione selezionata

:guilabel:`Ricalcola`
  Ricalcola l'intera valutazione selezionata, riesaminando tutti i
  risultati di tutti i tornei che la utilizzano

:guilabel:`Scarica`
  Permette di scaricare i dati di tutti i tornei che utilizzano la
  valutazione selezionata


Inserimento e modifica
~~~~~~~~~~~~~~~~~~~~~~

.. index::
   pair: Inserimento e modifica; Valutazioni Glicko

Ogni valutazione è identificata da una :guilabel:`descrizione` univoca, cioè non è possibile
inserire due diverse valutazioni con la medesima descrizione.

Il :guilabel:`livello` stabilisce in sostanza l'*importanza* della valutazione e la sua
*attendibilità*. Quando in un torneo associato a una certa valutazione viene stabilita la
valutazione di ciascun concorrente, viene usata la più recente nella valutazione di riferimento
**oppure** in una a livello *uguale o superiore*.

Il :guilabel:`tau` è il coefficiente primario per pilotare il calcolo della valutazione
nell'algoritmo Glicko2.

La :guilabel:`valutazione`, la :guilabel:`deviazione` e la :guilabel:`volatilità` sono i valori
di default della valutazione per un giocatori che partecipi per la prima volta a un torneo
associato alla valutazione.

.. important:: Questi valori risultano modificabili solo dall'amministratore del sistema: di
               norma **non** devono essere modificati, se non da chi sa come e perché farlo,
               oppure per fare esperimenti.

               In ogni caso, modificando questi valori rende necessario il ricalcolo della
               valutazione.
