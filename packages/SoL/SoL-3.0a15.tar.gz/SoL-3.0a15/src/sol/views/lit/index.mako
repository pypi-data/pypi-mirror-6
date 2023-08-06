## -*- coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    mer 17 dic 2008 02:16:28 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
from datetime import date
from sqlalchemy import distinct, func
from sol.models import Club, Player, Championship, Tourney

clubs = session.query(Club).filter(Club.championships.any()).order_by(Club.description).all()
nclubs = len(clubs)
ntourneys = session.query(func.count(Tourney.idtourney)).scalar()
nchampionships = session.query(func.count(Championship.idchampionship)).scalar()
nplayers = session.query(func.count(Player.idplayer)).scalar()
npcountries = session.query(func.count(distinct(Player.nationality))
                           ).filter(Player.nationality != None).scalar()
today = date.today()
%>

<%def name="title()">
  ${_('SoL Lit')}
</%def>

## Body

<dl>
  <dt>${_('Clubs')}</dt> <dd>${nclubs}</dd>
  <dt>${_('Championships')}</dt> <dd>${nchampionships}</dd>
  <dt>${_('Tourneys')}</dt> <dd>${ntourneys}</dd>
  <dt>${_('Players')}</dt> <dd>${nplayers} (${_('%d countries') % npcountries})</dd>
</dl>

% if clubs:
<h3>${_('Clubs')}</h3>
% endif

% for club in clubs:
<div class="club">
  % if club.emblem:
  <img class="emblem centered" src="/lit/emblem/${club.emblem}" />
  % else:
  <span class="spacer">&nbsp;</span>
  % endif

  <h4 class="centered">
    % if club.siteurl:
    <a href="${club.siteurl}" target="_blank">
    % endif
    ${club.description}
    % if club.siteurl:
    </a>
    % endif
  % if club.nationality:
    (<img src="/static/images/flags/${club.nationality}.png" />
    ${club.nationality})
  % endif
  </h4>

  <%
     singles = []
     doubles = []
     teams = []
     future = []
     for championship in club.championships:
         pt = []
         for t in championship.tourneys:
             if t.prized:
                 pt.append(t)
             elif t.date>today:
                 future.append(t)
         nt = len(pt)
         if nt:
             new = (today - pt[-1].date).days < 21
             if championship.playersperteam == 1:
                 singles.append((championship, nt, new))
             elif championship.playersperteam == 2:
                 doubles.append((championship, nt, new))
             else:
                 teams.append((championship, nt, new))
  %>
  % if singles:
  <h5>${_('Singles')}</h5>
  <ol>
    % for championship,nt,new in singles:
    <li class="championship">
      <a href="championshipranking?idchampionship=${championship.idchampionship}">
        ${championship.description}
      </a>
      (${ngettext('%d tourney', '%d tourneys', nt) % nt})
      % if new:
      <img src="/static/images/new.png" />
      % endif
    </li>
    % endfor
  </ol>
  % endif
  % if doubles:
  <h5>${_('Doubles')}</h5>
  <ol>
    % for championship,nt,new in doubles:
    <li class="championship">
      <a href="championshipranking?idchampionship=${championship.idchampionship}">
        ${championship.description}
      </a>
      (${ngettext('%d tourney', '%d tourneys', nt) % nt})
      % if new:
      <img src="/static/images/new.png" />
      % endif
    </li>
    % endfor
  </ol>
  % endif
  % if teams:
  <h5>${_('Teams')}</h5>
  <ol>
    % for championship,nt,new in teams:
    <li class="championship">
      <a href="championshipranking?idchampionship=${championship.idchampionship}">
        ${championship.description}
      </a>
      (${ngettext('%d tourney', '%d tourneys', nt) % nt})
      % if new:
      <img src="/static/images/new.png" />
      % endif
    </li>
    % endfor
  </ol>
  % endif
  % if future:
  <h5>${_('Future tourneys')}</h5>
  <ol>
    % for t in future:
    <li class="tourney">
      <a href="tourney?idtourney=${t.idtourney}">
        ${t.description} (${t.date.strftime(_('%m-%d-%Y'))})
      </a>
    </li>
    % endfor
  </ol>
  % endif
</div>
% endfor

<div class="clear" />
