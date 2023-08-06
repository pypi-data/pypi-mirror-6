## -*- coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    sab 13 dic 2008 16:34:14 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
import locale
from sol.models.utils import njoin
if entity.playersperteam==1:
    subject = _('Player')
else:
    subject = _('Team')
%>

<%def name="title()">
  ${entity.description}
</%def>

<%def name="club_emblem(url='', href='')">
  <%
     if entity.club.emblem:
         parent.club_emblem(url="/lit/emblem/%s" % entity.club.emblem,
                            href=entity.club.siteurl,
                            title=entity.club.description)
  %>
</%def>

<%def name="table_header(dates)">
      <thead>
        <tr>
          <td class="rank-header">#</td>
          <td class="player-header">${subject}</td>
          % for date in dates:
          <td class="event-header">
            <a href="tourney?idchampionship=${entity.idchampionship}&date=${date}">
              ${date.strftime(_('%m-%d-%y'))}
            </a>
          </td>
          % endfor
          <td class="sortedby total-header">${_('Total')}</td>
        </tr>
      </thead>
</%def>

<%def name="table_body(ranking)">
      <tbody>
        % for i, row in enumerate(ranking):
        ${table_row(i+1, row)}
        % endfor
      </tbody>
</%def>

<%def name="table_row(rank, row)">
        <tr class="${rank%2 and 'odd' or 'even'}-row">
          <td class="rank">${rank}</td>
          <td class="player">${njoin(row[0], stringify=lambda p: '<a href="player?idplayer=%d">%s</a>' % (p.idplayer, escape(p.caption(html=False)))) | n}</td>
          % for s in row[2]:
          <%
             if row[4] and s in row[4]:
                 eventclass = 'skipped-event'
                 row[4].remove(s)
             else:
                 eventclass = 'event'
          %>
          <td class="${eventclass}">${s and locale.format('%.2f', s) or ''}</td>
          % endfor
          <td class="sortedby total">${locale.format('%.2f', row[1])}</td>
        </tr>
</%def>

## Body

<dl>
  <dt>${_('Club')}</dt> <dd>${entity.club.description}</dd>
  <dt>${_('Players per team')}</dt> <dd>${entity.playersperteam}</dd>
  <% pmethod = entity.__class__.__table__.c.prizes.info['dictionary'][entity.prizes] %>
  <dt>${_('Prize-giving method')}</dt> <dd>${_(pmethod)}</dd>
  % if entity.skipworstprizes:
  <dt>${_('Skip worst prizes')}</dt> <dd>${entity.skipworstprizes}</dd>
  % endif
  % if entity.idprevious:
  <dt>${_('Previous championship')}</dt>
  <dd>
    <a href="championshipranking?idchampionship=${entity.idprevious}">
      ${entity.previous.description}
    </a>
  </dd>
  % endif
  % if entity.next:
  <dt>${_('Next championship')}</dt>
  <dd>
    <a href="championshipranking?idchampionship=${entity.next.idchampionship}">
      ${entity.next.description}
    </a>
  </dd>
  % endif
</dl>

<% dates, ranking = entity.championshipRanking() %>
<table class="ranking">
  <caption>${_('Championship ranking')} (<a href="/pdf/championshipranking?idchampionship=${entity.idchampionship}">pdf</a>) </caption>
  ${table_header(dates)}
  ${table_body(ranking)}
</table>
