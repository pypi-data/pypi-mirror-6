.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 12:24:45 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _autenticazione:

.. figure:: autenticazione.png
   :figclass: float-right

   Il pannello di autenticazione


Autenticazione
==============

Innanzitutto bisogna autenticarsi.

.. rubric:: *Ehi, ma che diavolo... ⁉⁈*

SoL è un'applicazione `client/server`, composta cioè da due
componenti. Da un lato c'è il *client*, una applicazione eseguita
all'interno di un moderno browser web grafico come Firefox__; questa
applicazione comunica con un *server* che effettivamente legge e
modifica il database e che implementa la cosiddetta `business
logic`__.

Le due parti comunicano tra loro attraverso una *connessione*, che può
essere sia **locale**, dove entrambe le parti vengono eseguite da una
**singola** macchina come due diversi programmi che girano in
parallelo, piuttosto che una connessione di **rete**, dove ci sono
**due** (o più) computer coinvolti, collegati a una `LAN`__ o
addirittura tramite Internet.

Questo consente tre diversi scenari:

1. il caso più semplice, una macchina sola a sè stante, senza alcuna
   connessione, magari solo una stampante: tutto si svolge su questa
   singola stazione;

2. alcuni computer connessi attraverso una ``LAN``, uno dei quali
   funge da server, dove si collegano uno o più client: immaginate di
   dover organizzare il Campionato Europeo, e di voler dare la
   possibilità ai giornalisti presenti di consultare l'andamento della
   gara direttamente dal loro laptop, magari collegato alla rete
   wireless locale...

3. il server è accessibile tramite Internet, quindi dall'esterno:
   magari solo per poter mostrare il campionato del vostro club, o
   addirittura per fornire un servizio on-line e consentire ad altre
   persone di organizzarsi e gestirsi il loro.

Quindi, per tornare alla domanda di partenza: sì, può essere un po'
una noia inserire le proprie credenziali, ma mi sembrano un giusto
pegno a fronte di queste possibilità.

Qualsiasi giocatore può essere autorizzato a connettersi, assegnandogli
un `nickname` e una password.

__ http://it.wikipedia.org/wiki/Business_logic
__ http://it.wikipedia.org/wiki/Local_area_network
__ https://www.mozilla.org/it/firefox/new/
