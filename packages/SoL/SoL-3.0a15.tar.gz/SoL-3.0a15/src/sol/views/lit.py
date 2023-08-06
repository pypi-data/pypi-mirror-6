# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Light user interface controller
# :Creato:    ven 12 dic 2008 09:18:37 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from datetime import date
import logging

from markupsafe import escape

from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from pyramid.view import view_config

from sqlalchemy.orm.exc import NoResultFound

from . import get_request_logger
from ..i18n import translatable_string as _, translator, gettext, ngettext
from ..models import (
    DBSession,
    Competitor,
    Player,
    Tourney,
    Championship,
    )
from ..models.errors import OperationAborted


logger = logging.getLogger(__name__)


@view_config(route_name="lit", renderer="lit/index.mako")
def index(request):
    return {"_": gettext,
            "ngettext": ngettext,
            "session": DBSession(),
            "version": request.registry.settings['desktop.version']}


def get_data(request, needsEntity=True):
    t = translator(request)

    try:
        sess = DBSession()
        params = request.params

        if 'idtourney' in params:
            try:
                idtourney = int(params['idtourney'])
            except ValueError:
                raise OperationAborted(
                    t(_('Invalid idtourney: $id',
                        mapping=dict(id=repr(params['idtourney'])))))
            entity = sess.query(Tourney).get(idtourney)
            if entity is None:
                raise OperationAborted(
                    t(_('Tourney $id does not exist',
                        mapping=dict(id=idtourney))))
        elif 'date' in params:
            try:
                idchampionship = int(params['idchampionship'])
            except:
                raise OperationAborted(
                    t(_('Invalid idchampionship: $id',
                        mapping=dict(id=repr(params.get('idchampionship'))))))
            try:
                eventdate = date(*[int(n) for n in params['date'].split('-')])
            except:
                raise OperationAborted(
                    t(_('Invalid date: $date',
                        mapping=dict(date=repr(params['date'])))))
            try:
                entity = sess.query(Tourney) \
                             .filter_by(idchampionship=idchampionship) \
                             .filter_by(date=eventdate).one()
            except NoResultFound:
                raise OperationAborted(
                    t(_('Tourney $date in championship $id does not exist',
                        mapping=dict(date=eventdate, id=idchampionship))))
        elif 'idchampionship' in params:
            try:
                idchampionship = int(params['idchampionship'])
            except ValueError:
                raise OperationAborted(
                    t(_('Invalid idchampionship: $id',
                        mapping=dict(id=repr(params['idchampionship'])))))
            entity = sess.query(Championship).get(idchampionship)
            if entity is None:
                raise OperationAborted(
                    t(_('Championship $id does not exist',
                        mapping=dict(id=idchampionship))))
        elif 'idplayer' in params:
            try:
                idplayer = int(params['idplayer'])
            except ValueError:
                raise OperationAborted(
                    t(_('Invalid idplayer: $id',
                        mapping=dict(id=repr(params['idplayer'])))))
            entity = sess.query(Player).get(idplayer)
            if entity is None:
                raise OperationAborted(
                    t(_('Player $id does not exist',
                        mapping=dict(id=idplayer))))
        elif needsEntity:
            raise OperationAborted(t(_('No subject specified')))

        return dict(
            _=gettext,
            entity=entity,
            escape=escape,
            ngettext=ngettext,
            request=request,
            session=sess,
            version=request.registry.settings['desktop.version'],
        )
    except OperationAborted as e:
        get_request_logger(request, logger).error("Couldn't create page: %s", e)
        raise HTTPBadRequest(str(e))
    except Exception as e:
        get_request_logger(request, logger).critical("Couldn't create page: %s", e,
                                                     exc_info=True)
        raise HTTPInternalServerError(str(e))


@view_config(route_name="lit_tourney", renderer="lit/tourney.mako")
def tourney(request):
    data = get_data(request)
    data["turn"] = request.params.get('turn')
    data["idplayer"] = request.params.get('idplayer')
    return data


@view_config(route_name="lit_player", renderer="lit/player.mako")
def player(request):
    return get_data(request)


@view_config(route_name="lit_championshipranking", renderer="lit/championshipranking.mako")
def championshipranking(request):
    return get_data(request)


def subscribe(self):
    from sol.lib.captcha import captcha

    ipaddress = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
    sas = self.sa_session

    # New session or bad guess? Retry
    if not 'captcha_secret' in session or session['captcha_secret'] != request.params.get('secret'):
        session['idtourney'] = request.params.get('idtourney')
        if session['idtourney'] is None:
            raise HTTPBadRequest(_('Invalid tourney.'))

        c.tourney = sas.query(Tourney).get(session['idtourney'])
        if c.tourney is None or c.tourney.prized or c.tourney.date <= date.today():
            raise HTTPBadRequest(_('Tourney is not open to subscriptions.'))

        session['captcha_secret'], c.captcha_uri = captcha()
        session.save()

        c.secret = None
        c.session = self.sa_session
        c.idtourney = session['idtourney']

        logger.info('New subscription challenge from %s', ipaddress)
        return render('/lit/subscribe.html')

    tourney = sas.query(Tourney).get(session['idtourney'])

    # Selected player, try to subscribe him
    if request.params.get('idplayer'):
        player = sas.query(Player).get(request.params['idplayer'])
    elif request.params.get('firstname') and request.params.get('lastname'):
        from sol.models.bio import _load_player

        player = _load_player(sas, lastname=request.params.get('lastname'),
                              firstname=request.params.get('firstname'),
                              sex=request.params.get('sex') or None,
                              nickname=None, nationality=None,
                              portrait=None, club=None,
                              create_new_if_missing=False)
    else:
        player = None

    if player is not None:
        # Known player: subscribe immediately

        competitor = Competitor()
        competitor.tourney = tourney
        competitor.player1 = player
        sas.add(competitor)
        sas.flush()

        session.namespace.remove()
        session.delete()

        self.report(_('Anonymous subscription notification'),
                    _('%(player)s has been subscribed to %(tourney)s') % dict(
                        player=player, tourney=tourney))

        redirect(url(controller='lit', action='tourney', idtourney=tourney.idtourney))

    elif request.params.get('firstname') and request.params.get('lastname'):
        # Unknown player: send a request to the administrator

        session.namespace.remove()
        session.delete()

        self.report(_('Anonymous subscription request'),
                    _('%(firstname)s %(lastname)s (%(sex)s) '
                      '(firstname/lastname/sex) would like to '
                      'partecipate to %(tourney)s') % dict(
                        firstname=request.params.get('firstname'),
                        lastname=request.params.get('lastname'),
                        sex=request.params.get('sex'),
                        tourney=tourney))

        return _("The indicated player, %(firstname)s %(lastname)s, "
                 "is not known to the system. A mail has been sent to "
                 "the administrator who will add him/her as soon as "
                 "possible. Thank you!") % dict(
            firstname=request.params.get('firstname'),
            lastname=request.params.get('lastname'))
    else:
        # Reshow the list of players
        c.session = self.sa_session
        c.idtourney = session['idtourney']
        c.tourney = tourney
        c.secret = session['captcha_secret']

        logger.info('Listing subscription candidates for %s', tourney)
        return render('/lit/subscribe.html')


def report(self, subject, message):
    import smtplib, email.utils
    from email.mime.text import MIMEText
    from socket import sslerror

    logger.info(message)

    gconf = config['global_conf']

    to_addresses = gconf.get('admin_email') or gconf.get('email_to')

    if not to_addresses:
        logger.warning('Set "[GLOBAL].admin_email" to activate notification')
        return

    if isinstance(to_addresses, (str, unicode)):
        to_addresses = [to_addresses]

    from_address = gconf.get('from_address', 'SoL@localhost')
    smtp_server = gconf.get('smtp_server', 'localhost')
    smtp_username = gconf.get('smtp_username')
    smtp_password = gconf.get('smtp_password')
    smtp_use_tls = gconf.get('smtp_use_tls')

    msg = render('/lit/notification.mako',
                 dict(message=message,
                      ipaddress=(request.environ.get('HTTP_X_FORWARDED_FOR') or
                                 request.environ.get('REMOTE_ADDR'))))
    msg = MIMEText(msg.encode('utf-8'), _charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = ', '.join(to_addresses)
    msg['Date'] = email.utils.formatdate()

    server = smtplib.SMTP(smtp_server)
    if smtp_use_tls:
        server.ehlo()
        server.starttls()
        server.ehlo()
    if smtp_username and smtp_password:
        server.login(smtp_username, smtp_password)
    result = server.sendmail(from_address, to_addresses, msg.as_string())
    if result:
        logger.error("Sendmail returned this: %s", result)
    try:
        server.quit()
    except sslerror:
        # sslerror is raised in tls connections on closing sometimes
        pass
