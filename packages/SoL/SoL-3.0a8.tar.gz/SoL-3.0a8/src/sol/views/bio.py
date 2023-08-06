# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Batched I/O controller
# :Creato:    lun 09 feb 2009 10:32:22 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from datetime import date
import logging

from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from pyramid.settings import asbool
from pyramid.view import view_config

from . import get_request_logger, unauthorized_for_guest
from ..i18n import translatable_string as _, ngettext, translator
from ..models import DBSession, Player, Rating, Championship, Tourney
from ..models.bio import dump_sol, load_sol, restore, save_changes
from ..models.errors import LoadError, OperationAborted
from ..models.utils import njoin


logger = logging.getLogger(__name__)


@view_config(route_name='backup')
def backup(request):
    "Backup almost everything in a ZIP file."

    from ..models.bio import backup

    settings = request.registry.settings
    response = request.response

    response.body = backup(DBSession(),
                           settings['sol.portraits_dir'],
                           settings['sol.emblems_dir'])
    response.content_type = 'application/zip'
    filename = '%s.zip' % date.today().isoformat()
    response.content_disposition = 'attachment; filename=%s' % filename

    return response


@view_config(route_name='dump')
def dump(request):
    "Dump tourneys in a portable format."

    from re import sub
    from sqlalchemy.orm import join

    params = request.params
    settings = request.registry.settings
    debug = asbool(settings['desktop.debug'])

    t = translator(request)

    try:
        sess = DBSession()

        compress = asbool(params.get('gzip', not debug))
        ext = 'sol.gz' if compress else 'sol'

        if 'idtourney' in params:
            idtourney = int(params['idtourney'])
            tourney = sess.query(Tourney).get(idtourney)
            if tourney is None:
                raise HTTPBadRequest(
                    t(_(u'Tourney $idtourney does not exist',
                        mapping=dict(idtourney=idtourney))))

            tourneys = [tourney]
            sdesc = tourneys[0].championship.description
            sdesc = sdesc.encode('ascii', 'ignore').decode('ascii')
            cturn = tourneys[0].currentturn
            filename = '%s-%s%s.%s' % (sub(r'\W+', '_', sdesc),
                                       str(tourneys[0].date),
                                       '+%d' % cturn if cturn else '',
                                       ext)
        elif 'idchampionship' in params:
            idchampionship = int(params['idchampionship'])
            tourneys = sess.query(Tourney) \
                       .filter_by(idchampionship=idchampionship).all()
            if not tourneys:
                raise HTTPBadRequest(
                    t(_(u'No tourneys in championship $idchampionship',
                        mapping=dict(idchampionship=idchampionship))))

            desc = tourneys[0].championship.description
            sdesc = desc.encode('ascii', 'ignore').decode('ascii')
            filename = '%s.%s' % (sub(r'\W+', '_', sdesc), ext)
        elif 'idclub' in params:

            idclub = int(params['idclub'])
            tourneys = sess.query(Tourney) \
                       .select_from(join(Tourney, Championship)) \
                       .filter(Championship.idclub == idclub).all()
            if not tourneys:
                raise HTTPBadRequest(
                    t(_(u'No tourneys organized by club $idclub',
                        mapping=dict(idclub=idclub))))

            desc = tourneys[0].championship.club.description
            cdesc = desc.encode('ascii', 'ignore').decode('ascii')
            filename = '%s.%s' % (sub(r'\W+', '_', cdesc), ext)
        else:
            tourneys = sess.query(Tourney).all()
            if not tourneys:
                raise HTTPBadRequest(t(_(u'No tourneys at all')))

            filename = '%s.%s' % (date.today().isoformat(), ext)

        response = request.response
        if compress:
            response.body = dump_sol(tourneys, compress)
            response.content_type = 'application/x-gzip'
        else:
            response.text = dump_sol(tourneys, compress)
            response.content_type = 'text/x-yaml'
        response.content_disposition = 'attachment; filename=%s' % filename

        return response

    except HTTPBadRequest as e:
        get_request_logger(request, logger).error(
            t(_(u"Couldn't dump tourney: $message",
                mapping=dict(message=str(e)))))
        raise

    except Exception as e:
        get_request_logger(request, logger).critical(
            t(_(u"Couldn't dump tourney: $message",
                mapping=dict(message=str(e)))), exc_info=True)
        raise HTTPInternalServerError(str(e))


@view_config(route_name='merge_players', renderer='json')
@unauthorized_for_guest
def mergePlayers(request):
    "Merge several players into a single one."

    t = translator(request)

    tid = int(request.params['tid'])
    sids = request.params.getall('sids')
    if not isinstance(sids, list):
        sids = [sids]
    sids = [int(i) for i in sids]

    sas = DBSession()
    player = sas.query(Player).get(tid)
    try:
        replaced = player.mergePlayers(sids)
    except OperationAborted as e:
        msg = str(e)
        get_request_logger(request, logger).error(
            t(_(u"Couldn't merge players: $message",
                mapping=dict(message=msg))))
        success = False
    except Exception as e:
        msg = str(e)
        get_request_logger(request, logger).exception(
            t(_(u"Couldn't merge players: $message",
                mapping=dict(message=msg))))
        success = False
    else:
        count = len(replaced)
        msg = ngettext(u'$count player has been merged into $player',
                       u'$count players has been merged into $player',
                       count, mapping=dict(count=count,
                                           player=player.caption(False)))
        success = True
    return dict(success=success, message=msg)


@view_config(route_name='save_changes', renderer='json')
@unauthorized_for_guest
def saveChanges(request):
    """Save changes made to a set of records."""

    from sqlalchemy.exc import DBAPIError, IntegrityError
    from metapensiero.sqlalchemy.proxy.json import json2py

    t = translator(request)

    params = request.params
    mr = json2py(params['modified_records'])
    dr = json2py(params['deleted_records'])

    sess = DBSession()

    success = False
    try:
        iids, mids, dids = save_changes(sess, request, mr, dr)
        sess.flush()
        success = True
        message = 'Ok'
        infomsg = []
        ni = len(iids)
        if ni:
            infomsg.append(
                ngettext(u'$count new record', u'$count new records', ni,
                         mapping=dict(count=ni)))
        nm = len(mids)
        if nm:
            infomsg.append(
                ngettext(u'$count changed record', u'$count changed records',
                         nm, mapping=dict(count=nm)))
        nd = len(dids)
        if nd:
            infomsg.append(
                ngettext(u'$count deleted record', u'$count deleted records',
                         nd, mapping=dict(count=nd)))
        if infomsg:
            get_request_logger(request, logger).info(
                t(_(u'Changes successfully committed: $changed',
                    mapping=dict(changed=njoin(infomsg)))))
    except OperationAborted as e:
        message = str(e)
        get_request_logger(request, logger).warning(
            t(_(u'Operation refused: $message',
                mapping=dict(message=message))))
    except IntegrityError as e:
        # Catch most common reasons, ugly as it is
        excmsg = str(e)
        if ('columns date, idchampionship are not unique' in excmsg
            or (' UNIQUE constraint failed:'
                ' tourneys.date, tourneys.idchampionship') in excmsg):
            get_request_logger(request, logger).warning(
                t(_(u'Not allowing duplicated event: $message',
                    mapping=dict(message=excmsg))))
            message = t(_(u'There cannot be two tourneys of the same'
                          u' championship on the same day, sorry!'))
        elif (' UNIQUE constraint failed:'
                ' championships.description, championships.idclub') in excmsg:
            get_request_logger(request, logger).warning(
                t(_(u'Not allowing duplicated championship: $message',
                    mapping=dict(message=excmsg))))
            message = t(_(u'There cannot be two championships with the same'
                          u' description organized by the same club!'))
        elif ' UNIQUE constraint failed: clubs.description' in excmsg:
            get_request_logger(request, logger).warning(
                t(_(u'Not allowing duplicated club: $message',
                    mapping=dict(message=excmsg))))
            message = t(_(u'There cannot be two clubs with the same'
                          u' description!'))
        elif ' UNIQUE constraint failed: ratings.description' in excmsg:
            get_request_logger(request, logger).warning(
                t(_(u'Not allowing duplicated rating: $message',
                    mapping=dict(message=excmsg))))
            message = t(_(u'There cannot be two ratings with the same'
                          u' description!'))
        elif ' UNIQUE constraint failed: championships.description' in excmsg:
            get_request_logger(request, logger).warning(
                t(_(u'Not allowing duplicated championship: $message',
                    mapping=dict(message=excmsg))))
            message = t(_(u'There cannot be two championships with the same'
                          u' description!'))
        elif (' UNIQUE constraint failed: players.nickname, players.firstname,'
              ' players.lastname') in excmsg:
            get_request_logger(request, logger).warning(
                t(_(u'Not allowing duplicated player: $message',
                    mapping=dict(message=excmsg))))
            message = t(_(u'There cannot be two players with the same'
                          u' firstname, lastname and nickname!'))
        elif (' may not be NULL' in excmsg
              or ' NOT NULL constraint failed' in excmsg):
            get_request_logger(request, logger).warning(
                t(_(u'Incomplete data: $message',
                    mapping=dict(message=excmsg))))
            message = t(_(u'Missing information prevents saving changes!'))
            message += "<br/>"
            message += t(_(u'Some mandatory fields were not filled in,'
                           u' please recheck.'))
        else:
            get_request_logger(request, logger).error(
                t(_(u'Could not save changes: $message',
                    mapping=dict(message=excmsg))))
            message = t(_(u'Integrity error prevents saving changes!'))
            message += "<br/>"
            message += t(_(u'Most probably a field contains an invalid value:'
                           u' consult the application log for details.'))
    except DBAPIError as e:
        get_request_logger(request, logger).error(
            t(_(u'Could not save changes: $message',
                mapping=dict(message=str(e)))))
        message = t(_(u'Error occurred while saving changes!'))
        message += "<br/>"
        message += t(_(u'Please inform the admin or consult'
                       u' the application log.'))
    except Exception as e:
        get_request_logger(request, logger).critical(
            t(_(u'Could not save changes: $message',
                mapping=dict(message=str(e)))))
        message = t(_(u'Internal error!'))
        message += "<br/>"
        message += t(_(u'Please inform the admin or consult'
                       u' the application log.'))

    return dict(success=success, message=message)


@view_config(route_name='upload')
def upload(request):
    "Handle the upload of tourneys data."

    from metapensiero.sqlalchemy.proxy.json import py2json

    t = translator(request)

    settings = request.registry.settings
    params = request.params
    archive = params.get('archive')

    success = False
    load = None

    if archive is not None:
        fnendswith = archive.filename.endswith

        if fnendswith('.sol') or fnendswith('.sol.gz'):
            load = load_sol
        elif fnendswith('.zip'):
            if request.session['user_name'] == settings['sol.admin.user']:
                load = lambda sasess, url, content: restore(
                    sasess,
                    settings['sol.portraits_dir'], settings['sol.emblems_dir'],
                    url, content)
            else:
                msg = t(_(u'Only admin can restore whole ZIPs, sorry!'))
                get_request_logger(request, logger).warning(
                    t(_('Attempt to restore $file rejected',
                        mapping=dict(file=archive.filename))))
        else:
            msg = t(_(u'Unknown file type: $file',
                      mapping=dict(file=archive.filename)))
            get_request_logger(request, logger).warning(
                t(_('Attempt to upload $file rejected',
                    mapping=dict(file=archive.filename))))
    else:
        msg = t(_(u'Required "archive" parameter is missing!'))

    if load is not None:
        sas = DBSession()
        try:
            res = load(sas, url=archive.filename, content=archive.file)
            sas.flush()
            if res:
                if isinstance(res, dict):
                    msg = res['message']
                    get_request_logger(request, logger).warning(msg)
                    success = False
                else:
                    msg = ngettext(
                        u'Successfully loaded $num tourney',
                        u'Successfully loaded $num tourneys',
                        len(res), mapping=dict(num=len(res)))
                    success = True
            else:
                msg = t(_(u'No new tourney found!'))
                success = False
        except (LoadError, OperationAborted) as e:
            msg = str(e)
            success = False
            get_request_logger(request, logger).error(
                t(_(u'Upload of $file failed: $msg',
                    mapping=dict(file=archive.filename, msg=msg))))
        except Exception as e:
            msg = str(e)
            success = False
            get_request_logger(request, logger).exception(
                t(_(u'Upload of $file failed: $msg',
                    mapping=dict(file=archive.filename, msg=msg))))
        else:
            get_request_logger(request, logger).info(
                t(_(u'Successful upload of $file: $msg',
                    mapping=dict(file=archive.filename, msg=msg))))

    # The answer must be "text/html", even if we really return JSON:
    # see the remark regarding `fileUpload` in the ExtJS BasicForm.js

    response = request.response
    response.content_type = 'text/html'
    response.text = py2json(dict(success=success, message=msg))

    return response


@view_config(route_name='recompute_rating', renderer='json')
@unauthorized_for_guest
def recomputeRating(request):
    "Recompute a whole Rating."

    t = translator(request)

    rid = int(request.params['idrating'])

    sas = DBSession()
    rating = sas.query(Rating).get(rid)
    if rating is None:
        raise HTTPBadRequest(
            t(_(u'Rating $idrating does not exist',
                mapping=dict(idrating=rid))))
    else:
        try:
            rating.recompute(scratch=True)
        except Exception as e:
            msg = str(e)
            get_request_logger(request, logger).exception(
                t(_(u"Couldn't recompute rating: $message",
                    mapping=dict(message=msg))))
            success = False
        else:
            msg = t(_(u'Recomputed rating “$rating”',
                      mapping=dict(rating=rating.caption(False))))
            get_request_logger(request, logger).info(msg)
            success = True
    return dict(success=success, message=msg)
