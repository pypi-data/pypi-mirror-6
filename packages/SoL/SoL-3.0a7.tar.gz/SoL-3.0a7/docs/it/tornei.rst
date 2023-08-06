.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:13:43 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _gestione tornei:

Gestione tornei
---------------

.. index::
   pair: Gestione; Tornei

Il *torneo* è chiaramente l'elemento primario di tutto il sistema,
tutto quanto verte a permettere di gestire in maniera facile e veloce
questi eventi.


Voci del menu
~~~~~~~~~~~~~

Oltre alle :ref:`azioni standard <pulsanti-standard>` il menu contiene
queste voci:

.. figure:: tornei.png
   :figclass: float-right

   Gestione tornei

:guilabel:`Dettagli`
  Mostra la :ref:`gestione <gestione torneo>` del torneo selezionato.

:guilabel:`Concorrenti`
  Consente di :ref:`correggere i concorrenti <correzione concorrenti>`
  di un torneo già svolto.

:guilabel:`Rigioca di nuovo`
  Consente di *duplicare* un torneo: particolarmente utile nei tornei
  di doppio o a squadre: in pratica replica il torneo sul giorno
  corrente, con tutti i suoi concorrenti; assicurati di aggiornarne la
  descrizione ed eventualmente la data dell'evento!

:guilabel:`Scarica`
  Permette di scaricare i dati del torneo.


Inserimento e modifica
~~~~~~~~~~~~~~~~~~~~~~

.. index::
   pair: Inserimento e modifica; Tornei

Ogni torneo ha una :guilabel:`data` e una :guilabel:`descrizione`
dell'evento e non ci possono essere due distinti tornei nella stessa
data associati al medesimo campionato.

Il :guilabel:`posto` è opzionale.

:guilabel:`Durata` e :guilabel:`preavviso` si riferiscono alla durata
di un singolo turno e sono espressi in *minuti*. Vengono usati per
visualizzare l':ref:`orologio`.

Un torneo può essere associato a una particolare
:guilabel:`valutazione`: in questo caso il primo turno verrà generato
tenendo conto del valore di ciascun giocatore invece che usando un
ordine casuale.

.. _accoppiamenti:

Il :guilabel:`metodo accoppiamenti` determina come verranno create le
coppie di avversari ad ogni nuovo turno:

``Classifica``
  l'algoritmo ``serial`` cercherà di accoppiare un giocatore con uno
  di quelli che lo seguono nella classifica corrente, ad esempio il
  primo col secondo, il terzo con il quarto e così via;

``Classifica sfasata``
  per ritardare per quanto possibile gli incontri tra le teste di
  serie, questo metodo (``dazed``) usa un sistema più elaborato:
  prende i giocatori a pari punti di quello che sta esaminando e cerca
  di accoppiare il primo con quello che sta a metà di questa serie, il
  secondo con quello a metà+1, e così via.

.. toctree::
   :maxdepth: 2

   torneo
   concorrenti
