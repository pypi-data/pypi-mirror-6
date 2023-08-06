## -*- coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    mer 14 ott 2009 15:04:33 CEST
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.html" />

<%
from sol import i18n
if c.secret:
    from datetime import date
    today = date.today()

    from sqlalchemy import not_
    from sol.models import Player
    available_players = c.session.query(Player)
    subscribed = [p.idplayer for p in c.tourney.allPlayers()]
    if subscribed:
        available_players = available_players.filter(not_(Player.idplayer.in_(subscribed)))
    players = ((p.idplayer, p.caption(html=False))
               for p in available_players.order_by(Player.lastname, Player.firstname))
%>

<%def name="title()">
  ${_('Tourney subscription')}
</%def>

<%def name="header()">
  ${parent.header()}
  <h2 class="subtitle centered">
    ${c.tourney.description}
  </h2>
</%def>

<%def name="club_emblem(url='', href='')">
  <%
     if c.tourney.championship.club.emblem:
         parent.club_emblem(url="emblem/%s" % c.tourney.championship.club.emblem,
                            href=c.tourney.championship.club.siteurl,
                            title=c.tourney.championship.club.description)
  %>
</%def>


## Body

<dl>
  <dt>${_('Location')}</dt> <dd>${c.tourney.location}</dd>
  <dt>${_('Date')}</dt> <dd>${c.tourney.date.strftime(str(_('%m-%d-%Y')))}</dd>
  % if c.tourney.prizefactor!=1:
  <dt>${_('Prize factor')}</dt> <dd>${locale.format('%.2f', c.tourney.prizefactor)}</dd>
  % endif
  <dt>${_('Championship')}</dt> <dd>${c.tourney.championship.description}</dd>
</dl>

% if not c.secret:
<p>${_('Welcome to the self-subscription service for the tourney.')}</p>
<p>${_('The first step is an annoying measure that should prevent most unwanted requests, thank you for the patience.')}</p>
<p>${_('Simply insert the obfuscated number you see below and hit the %(subscribe)s button.') % dict(subscribe=_('subscribe'))}</p>
% else:
<p>${_('Ok, next step: select the player you want subscribed to the given tourney and hit the %(subscribe)s button.') % dict(subscribe=_('subscribe'))}
  ${_("Please double check the choice before confirmation, because you'll have no way to unsubscribe the player other than contacting the administrator.")}</p>
<p>${_('If you cannot find his/her name in the list, enter the full name and hit the %(register)s button:') % dict(register=_('register'))}
  ${_('a request for subscription will be sent to the administrator.')}</p>
% endif

<form>
  <input type="hidden" name="idtourney" id="idtourney" value="${c.idtourney}" />
  % if c.secret:
  <input type="hidden" name="secret" id="secret" value="${c.secret}" />
  % endif

  <table>
    % if not c.secret:
    <tr>
      <th><label for="secret">${ _("Captcha number") }</label></th>
      <td><input type="text" name="secret" id="secret" /></td>
    </tr>
    <tr>
      <th />
      <td>
        <img src="${c.captcha_uri}" />
      </td>
    </tr>
    % else:
    <tr>
      <th><label for="player">${ _("Player") }</label></th>
      <td>
        <select size="20" name="idplayer">
          % for p in players:
          <option value="${p[0]}">${p[1]}</option>
          % endfor
        </select>
      </td>
    </tr>
    % endif
    <tr>
      <th><label for="submit"></label></th>
      <td><button name="submit" type="submit" id="submit" value="subscribe">${ _("subscribe") }</button></td>
    </tr>
    % if c.secret:
    <tr>
      <th><label for="firstname">${_("First name")}</label></th>
      <td><input type="text" name="firstname" id="firstname" /></td>
    </tr>
    <tr>
      <th><label for="lastname">${_("Last name")}</label></th>
      <td><input type="text" name="lastname" id="lastname" /></td>
    </tr>
    <tr>
      <th><label for="sex">${_("Sex")}</label></th>
      <td>
        <select name="sex">
          <option value="F">${_("Female")}</option>
          <option value="M">${_("Male")}</option>
        </select>
      </td>
    </tr>
    <tr>
      <th><label for="register"></label></th>
      <td><button name="submit" type="submit" id="register" value="register">${ _("register") }</button></td>
    </tr>
    % endif
  </table>
</form>
