## -*- coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    sab 13 dic 2008 16:34:51 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
from datetime import date
import locale
from sol.models.utils import njoin
if entity.championship.playersperteam==1:
    subject = _('Player')
else:
    subject = _('Team')
%>

<%def name="title()">
  ${entity.description}
</%def>

<%def name="header()">
  ${parent.header()}
  <h2 class="subtitle centered">
    <a href="championshipranking?idchampionship=${entity.championship.idchampionship}">
      ${entity.championship.description}
    </a>
  </h2>
</%def>

<%def name="club_emblem(url='', href='')">
  <%
     if entity.championship.club.emblem:
         parent.club_emblem(url="/lit/emblem/%s" % entity.championship.club.emblem,
                            href=entity.championship.club.siteurl,
                            title=entity.championship.club.description)
  %>
</%def>


## Body

<dl>
  <dt>${_('Location')}</dt> <dd>${entity.location}</dd>
  <dt>${_('Date')}</dt> <dd>${entity.date.strftime(_('%m-%d-%Y'))}</dd>
  % if turn is not None or idplayer is not None:
  <dt>${_('Duration')}</dt> <dd>${ngettext('%d minute', '%d minutes', entity.duration) % entity.duration}</dd>
  <% cmethod = entity.__class__.__table__.c.couplings.info['dictionary'][entity.couplings] %>
  <dt>${_('Coupling method')}</dt> <dd>${_(cmethod)}</dd>
  % else:
  % endif
  <% pmethod = entity.championship.__class__.__table__.c.prizes.info['dictionary'][entity.championship.prizes] %>
  <dt>${_('Prize-giving method')}</dt> <dd>${_(pmethod)}</dd>
  % if entity.rankedturn:
  <dt>${_('Turns')}</dt> <dd>${', '.join(['<a href="tourney?idtourney=%d&turn=%d">%d</a>'%(entity.idtourney,i,i) for i in range(1,entity.rankedturn+1)]) | n}</dd>
  % if turn is not None:
  <dt>${_('Ranked turn')}</dt>
  <dd>
    <a href="tourney?idtourney=${entity.idtourney}">
      ${entity.rankedturn}
    </a>
  </dd>
  % endif
  % endif
</dl>

% if turn is None and idplayer is None:

<%def name="ranking_header()">
      <thead>
        <tr>
          <td class="rank-header">#</td>
          <td class="player-header">${subject}</td>
          % if entity.rankedturn:
          <td class="event-header">${_('Points')}</td>
          <td class="event-header">${_('Bucholz')}</td>
          <td class="event-header">${_('Net score')}</td>
          <td class="event-header">${_('Total score')}</td>
          % endif
          % if entity.prized:
          <td class="sortedby total-header">${_('Final prize')}</td>
          % endif
        </tr>
      </thead>
</%def>

<%def name="ranking_body(ranking)">
      <tbody>
        % for i, row in enumerate(ranking):
        ${ranking_row(i+1, row)}
        % endfor
      </tbody>
</%def>

<%def name="ranking_row(rank, row)">
        <tr class="${rank%2 and 'odd' or 'even'}-row">
          <td class="rank">${rank}</td>
          <% players = [getattr(row, 'player%d'%i) for i in range(1,5) if getattr(row, 'player%d'%i) is not None] %>
          <td class="player">${njoin(players, stringify=lambda p: '<a href="player?idplayer=%d">%s</a>' % (p.idplayer, escape(p.caption(html=False)))) | n}</td>
          % if entity.rankedturn:
          <td class="event">${row.points}</td>
          <td class="event">${row.bucholz}</td>
          <td class="event">${row.netscore}</td>
          <td class="event">${row.totscore}</td>
          % endif
          % if entity.prized:
          <td class="sortedby total">${row.prize}</td>
          % endif
        </tr>
</%def>

<% ranking = entity.ranking %>
<table class="ranking">
  <caption>
  % if entity.prized or entity.date <= date.today():
  ${_('Ranking')} (<a href="/pdf/ranking?idtourney=${entity.idtourney}">pdf</a>)
  % else:
  ${_('Current competitors')} (<a href="subscribe?idtourney=${entity.idtourney}"> ${_('Subscribe now!')} </a>)
  % endif
  </caption>
  ${ranking_header()}
  ${ranking_body(ranking)}
</table>

% else:

<%def name="matches_header()">
      <thead>
        <tr>
          <td class="rank-header">#</td>
          <td colspan="3" class="competitors-header">${_('Competitors')}</td>
          <td colspan="3" class="scores-header">${_('Score')}</td>
        </tr>
      </thead>
</%def>

<%def name="matches_body(matches)">
      <tbody>
        % for i, row in enumerate(matches):
        ${matches_row(i+1, row)}
        % endfor
      </tbody>
</%def>

<%def name="matches_row(rank, row)">
        <% base = 'tourney?idtourney=%d&' % row.tourney.idtourney %>
        <tr class="${rank%2 and 'odd' or 'even'}-row">
          <td class="rank">${rank}</td>
          <%
             ctor = row.competitor1
             players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
          %>
          <td class="competitor1${row.score1>row.score2 and ' winner' or ''}">${njoin(players, stringify=lambda p: '<a href="%sidplayer=%d">%s</a>' % (base, p.idplayer, escape(p.caption(html=False)))) | n}</td>
          <td class="separator"></td>
          % if row.idcompetitor2:
          <%
             ctor = row.competitor2
             players = [ctor.player1, ctor.player2, ctor.player3, ctor.player4]
          %>
          <td class="competitor2${row.score1<row.score2 and ' winner' or ''}">${njoin(players, stringify=lambda p: '<a href="%sidplayer=%d">%s</a>' % (base, p.idplayer, escape(p.caption(html=False)))) | n}</td>
          % else:
          <td class="phantom">${_('Phantom')}</td>
          % endif
          <td class="score1${row.score1>row.score2 and ' winner' or ''}">${row.score1}</td>
          <td class="separator"></td>
          <td class="score2${row.score1<row.score2 and ' winner' or ''}">${row.score2}</td>
        </tr>
</%def>

<%
   if idplayer:
       idp = int(idplayer)
       matches = [m for m in entity.matches
                  if (m.competitor1.idplayer1 == idp or
                      m.competitor1.idplayer2 == idp or
                      m.competitor1.idplayer3 == idp or
                      m.competitor1.idplayer4 == idp or
                      (m.competitor2 and (m.competitor2.idplayer1 == idp or
                                          m.competitor2.idplayer2 == idp or
                                          m.competitor2.idplayer3 == idp or
                                          m.competitor2.idplayer4 == idp)))]
       if matches:
           m0 = matches[0]
           if (m0.competitor1.idplayer1 == idp or
               m0.competitor1.idplayer2 == idp or
               m0.competitor1.idplayer3 == idp or
               m0.competitor1.idplayer4 == idp):
               cname = m0.competitor1.caption(html=False)
           else:
               cname = m0.competitor2.caption(html=False)
           caption = _('Matches of %s') % ('<a href="player?idplayer=%d">%s</a>' % (idp, escape(cname)))
       else:
           caption = _('No matches for this player')
   else:
       matches = [m for m in entity.matches if m.turn == int(turn)]
       caption = _('Turn no. %s') % turn
%>

<table class="matches">
  <caption>${caption | n}</caption>
  ${matches_header()}
  ${matches_body(matches)}
</table>

% endif
