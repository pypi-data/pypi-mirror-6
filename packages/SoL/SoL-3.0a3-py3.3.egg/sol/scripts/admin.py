# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Configuration tool
# :Creato:    gio 18 apr 2013 18:43:18 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from argparse import ArgumentParser
from binascii import hexlify
from datetime import date
from os import urandom
from os.path import abspath, dirname, exists, join
from urllib.request import urlopen

from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import transaction

from pyramid.paster import get_appsettings, setup_logging

from sol.models import Base, Club, DBSession, Player, Rate, Rating, bio
from sol.models.utils import normalize


def create_config(args):
    "Dump a configuration file suitable for production"

    import sol

    if exists(args.config):
        print('The config file "%s" already exists!' % args.config)
        return None

    alembicdir = join(dirname(dirname(sol.__file__)), 'alembic')
    secret = hexlify(urandom(20)).decode('ascii')
    password = hexlify(urandom(5)).decode('ascii')

    with open(join(dirname(__file__), "config.tpl"), encoding='utf-8') as f:
        configuration = f.read()

    with open(args.config, 'w', encoding='utf-8') as f:
        f.write(configuration.format(secret=secret, password=password,
                                     alembicdir=alembicdir))

    print('The configuration file "%s" has been successfully created' % args.config)
    print('The password for the admin user is "%s", you should change it!' % password)

def initialize_db(args):
    "Initialize the database structure"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    setup_logging(args.config)
    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    print('The database "%s" has been successfully initialized or upgraded'
          % engine.url)

    from alembic.config import Config
    from alembic import command

    cfg = Config(args.config, ini_section="app:main")
    command.stamp(cfg, "head")


def upgrade_db(args):
    "Upgrade the database structure"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    from alembic.config import Config
    from alembic import command

    setup_logging(args.config)
    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    cfg = Config(args.config, ini_section="app:main")
    command.upgrade(cfg, "head")


def restore_all(args):
    "Load historic data into the database, player's portraits and club's emblems as well"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    setup_logging(args.config)
    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    sasess = DBSession()
    pdir = settings['sol.portraits_dir']
    edir = settings['sol.emblems_dir']

    if args.url.startswith('file://') or exists(args.url):
        if not args.url.startswith('file://'):
            args.url = abspath(args.url)
        backup_url = args.url
    else:
        backup_url = args.url + 'bio/backup'

    print("Loading backup from %s..." % backup_url)

    with transaction.manager:
        tourneys = bio.restore(sasess, pdir, edir, url=backup_url)

    print("Done, %d new/updated tourneys." % len(tourneys))


def backup_all(args):
    "Save a backup of the database, player's portraits and club's emblems as well"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    setup_logging(args.config)
    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    sasess = DBSession()
    pdir = settings['sol.portraits_dir']
    edir = settings['sol.emblems_dir']

    print("Saving backup to %s..." % args.location)

    with transaction.manager:
        bio.backup(sasess, pdir, edir,
                   args.location, args.keep_only_if_changed)

    print("Done.")


def player_unique_hash(firstname, lastname, nickname):
    from hashlib import md5
    from time import time

    hash = md5()
    hash.update(firstname.encode('ascii', 'ignore'))
    hash.update(lastname.encode('ascii', 'ignore'))
    hash.update(nickname.encode('ascii', 'ignore'))
    hash.update(str(time()).encode('ascii', 'ignore'))
    return hash.hexdigest()[:15]


def load_historical_rating(args):
    "Load historic rating into the database"

    if not exists(args.config):
        print('The config file "%s" does not exist!' % args.config)
        return 128

    fmap = dict(firstname='firstname',
                lastname='lastname',
                nickname='nickname',
                rate='rate')
    for item in args.map:
        internal, external = item.split('=')
        internal = internal.strip()
        external = external.strip()
        fmap[internal] = external

    refdate = date(*map(int, args.date.split('-')))

    setup_logging(args.config)
    settings = get_appsettings(args.config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    sasess = DBSession()

    if sasess.query(Rating).filter_by(description=args.description).first():
        print('Rating "%s" already exists!' % args.description)
        return 128

    if args.url.startswith('file://') or exists(args.url):
        if not args.url.startswith('file://'):
            args.url = abspath(args.url)

    print("Loading ratings from %s..." % args.url)

    separator = '\t' if args.tsv else ','

    done = set()
    rates = []
    with transaction.manager, urlopen(args.url) as csvfile:
        data = csvfile.read().decode(args.encoding)
        lines = data.splitlines()
        columns = [c.strip() for c in lines.pop(0).split(separator)]
        for c in fmap.values():
            if not c in columns:
                print('Column "%s" not found!' % c)
                return 128

        for record in (dict(zip(columns, row.split(separator))) for row in lines):
            firstname = normalize(record[fmap['firstname']].strip())
            lastname = normalize(record[fmap['lastname']].strip())
            nickname = record[fmap['nickname']].strip()

            if (firstname, lastname, nickname) in done:
                continue

            done.add((firstname, lastname, nickname))

            try:
                player, merged_into = Player.find(sasess, lastname, firstname, nickname)
            except MultipleResultsFound:
                nickname = player_unique_hash(firstname, lastname, nickname)

            if player is None:
                player = Player(firstname=firstname, lastname=lastname, nickname=nickname)
                if 'sex' in fmap:
                    sex = record[fmap['sex']].strip().upper()
                    if sex in 'FM':
                        player.sex = sex
                if 'club' in fmap:
                    clubdesc = normalize(record[fmap['club']].strip())
                    if clubdesc:
                        try:
                            club = sasess.query(Club).filter_by(description=clubdesc).one()
                        except NoResultFound:
                            club = Club(description=clubdesc)

                        player.club = club

            rate = int(record[fmap['rate']])
            rates.append(Rate(date=refdate, player=player, rate=rate,
                              deviation=int(args.deviation),
                              volatility=args.volatility))

        rating = Rating(description=args.description, level='0', rates=rates)
        sasess.add(rating)

    print("Done, %d new rates." % len(rates))


def _sound(which, mp3):
    from shutil import copyfile

    if not exists(mp3):
        print('Specified sound file "%s" does not exist!' % mp3)
        return 128
    if not mp3.endswith('.mp3'):
        print('The sound file must be a MP3 and have ".mp3" as extension!')
        return 128

    target = join(dirname(dirname(abspath(__file__))), 'static', 'sounds',
                  which+'.mp3')
    print('Copying "%s" to "%s"...' % (mp3, target))
    copyfile(mp3, target)


def start_sound(args):
    "Replace the start sound"

    return _sound('start', args.sound)


def stop_sound(args):
    "Replace the stop sound"

    return _sound('stop', args.sound)


def prealarm_sound(args):
    "Replace the prealarm sound"

    return _sound('prealarm', args.sound)


def main():
    import sys

    parser = ArgumentParser(description="SoL command line admin utility",
                            epilog=('You can get individual commands help'
                                    ' with "soladmin sub-command -h".'))
    subparsers = parser.add_subparsers()

    subp = subparsers.add_parser('create-config',
                                 help=create_config.__doc__)
    subp.add_argument('config', help="Name of the new configuration file")
    subp.set_defaults(func=create_config)

    subp = subparsers.add_parser('initialize-db',
                                 help=initialize_db.__doc__)
    subp.add_argument('config', help="Name of the configuration file")
    subp.set_defaults(func=initialize_db)

    subp = subparsers.add_parser('upgrade-db',
                                 help=upgrade_db.__doc__)
    subp.add_argument('config', help="Name of the configuration file")
    subp.set_defaults(func=upgrade_db)

    subp = subparsers.add_parser('restore',
                                 help=restore_all.__doc__)
    subp.add_argument('config', help="Name of the configuration file")
    subp.add_argument('url', default="http://sol.metapensiero.it/",
                      nargs="?",
                      help=('URL from where historic data will be loaded'
                            ' if different from "http://sol.metapensiero.it/".'
                            ' It may also be a file:// URI or a local file path'
                            ' name.'))
    subp.set_defaults(func=restore_all)

    subp = subparsers.add_parser('backup',
                                 help=backup_all.__doc__)
    subp.add_argument('-k', '--keep-only-if-changed', default=False,
                      action="store_true",
                      help="If given, and the location argument is a"
                      " directory containing other backup archives,"
                      " keep the new backup only if it is different"
                      " from the previous one.")
    subp.add_argument('config', help="Name of the configuration file")
    subp.add_argument('location', nargs="?", default='.',
                      help='Local file name where the backup will be written.'
                      ' If it actually points to an existing directory (its'
                      ' default value is ".", the current working directory)'
                      ' the file name will be generated from the current time'
                      ' and with a ".zip" extension.')
    subp.set_defaults(func=backup_all)

    subp = subparsers.add_parser('load-historical-rating',
                                 help=load_historical_rating.__doc__)
    subp.add_argument('--date', default='1900-01-01',
                      help="Bogus rates date, by default 1900-01-01")
    subp.add_argument('--deviation', default='100',
                      help="Value of the deviation, by default 100")
    subp.add_argument('--volatility', default='0.006',
                      help="Value of the volatility, by default 0.006")
    subp.add_argument('--description',
                      help='Description of the historical rating')
    subp.add_argument('--map', action='append', default=[],
                        help="Specify a map between internal (SoL) field name and"
                        " external one")
    subp.add_argument('--encoding', default='utf-8',
                      help="Encoding of the CSV file, by default UTF-8")
    subp.add_argument('--tsv', default=False, action="store_true",
                      help="Fields are separated by a TAB, not by a comma")
    subp.add_argument('config', help="Name of the configuration file")
    subp.add_argument('url',
                      help="URL from where historic CSV data will be loaded."
                      " It may also be a file:// URI or a local file path"
                      " name.")
    subp.set_defaults(func=load_historical_rating)

    subp = subparsers.add_parser('start-sound',
                                 help=start_sound.__doc__)
    subp.add_argument('sound', help="Name of the new MP3 sound file")
    subp.set_defaults(func=start_sound)

    subp = subparsers.add_parser('stop-sound',
                                 help=stop_sound.__doc__)
    subp.add_argument('sound', help="Name of the new MP3 sound file")
    subp.set_defaults(func=stop_sound)

    subp = subparsers.add_parser('prealarm-sound',
                                 help=prealarm_sound.__doc__)
    subp.add_argument('sound', help="Name of the new MP3 sound file")
    subp.set_defaults(func=prealarm_sound)

    args = parser.parse_args()
    sys.exit(args.func(args) if hasattr(args, 'func') else 0)


if __name__ == '__main__':
    main()
