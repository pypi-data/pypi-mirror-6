# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Test basic I/O
# :Creato:    mar 10 feb 2009 10:23:48 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import transaction

from sqlalchemy.orm.exc import NoResultFound

from sol import models
from sol.tests import TestCase
from sol.models.bio import save_changes
from sol.models.errors import OperationAborted


class TestBasicIO(TestCase):

    def test_insert(self):
        s = models.DBSession()

        i, m, d = save_changes(s, None, [
            ('idplayer', dict(firstname='New',
                              lastname='user',
                              nickname='test',
                              password='test')),
            ], [])
        s.flush()
        self.assertEqual(len(i), 1)
        self.assertEqual(len(m), 0)
        self.assertEqual(len(d), 0)

        new = s.query(models.Player).get(i[0]['idplayer'])
        self.assertEqual(new.firstname, 'New')
        self.assertEqual(new.lastname, 'User')
        self.assertEqual(new.nickname, 'test')
        self.assertNotEqual(new.password, 'test')

    def test_delete(self):
        s = models.DBSession()

        try:
            i, m, d = save_changes(s, None, [], [('idplayer', 1)])
        except OperationAborted:
            pass
        else:
            assert False, "Should raise an exception, player is playing!"
        s.rollback()

        i, m, d = save_changes(s, None, [
            ('idplayer', dict(firstname='New',
                              lastname='user',
                              nickname='test',
                              password='test')),
            ], [])
        s.flush()
        self.assertEqual(len(i), 1)
        self.assertEqual(len(m), 0)
        self.assertEqual(len(d), 0)

        tbdid = i[0]['idplayer']
        i, m, d = save_changes(s, None, [], [('idplayer', tbdid)])
        s.flush()
        self.assertEqual(len(i), 0)
        self.assertEqual(len(m), 0)
        self.assertEqual(len(d), 1)

        deleted = s.query(models.Player).get(tbdid)
        self.assertIs(deleted, None)

    def test_modify(self):
        s = models.DBSession()

        i, m, d = save_changes(s, None, [
            ('idplayer', dict(idplayer=1,
                              password='test')),
            ], [])
        s.flush()
        self.assertEqual(len(i), 0)
        self.assertEqual(len(m), 1)
        self.assertEqual(len(d), 0)

        chg = s.query(models.Player).get(m[0]['idplayer'])
        self.assert_(chg.password is not None and chg.password != 'test')

    def test_insert_and_modify(self):
        from . import PlayerData, TourneyData

        s = models.DBSession()

        t = s.query(models.Tourney).filter_by(
            description=TourneyData.double.description).one()

        lele = s.query(models.Player).filter_by(
            firstname=PlayerData.lele.firstname).one()

        bob = s.query(models.Player).filter_by(
            firstname=PlayerData.bob.firstname).one()

        fata = s.query(models.Player).filter_by(
            firstname=PlayerData.fata.firstname).one()

        leleteam = s.query(models.Competitor).filter_by(
            idtourney=t.idtourney, idplayer1=lele.idplayer).one()

        with transaction.manager:
            i, m, d = save_changes(s, None, [
                ('idcompetitor', dict(idcompetitor=0,
                                      idtourney=t.idtourney,
                                      idplayer1=bob.idplayer,
                                      idplayer2=fata.idplayer)),
                ('idcompetitor', dict(idcompetitor=leleteam.idcompetitor,
                                      idplayer2=None))
                ], [])
            s.flush()

        self.assertEqual(len(i), 1)
        self.assertEqual(len(m), 1)
        self.assertEqual(len(d), 0)

        s = models.DBSession()

        t = s.query(models.Tourney).filter_by(
            description=TourneyData.double.description).one()
        competitors = t.competitors
        self.assertEqual(len(competitors), 3)
        for c in competitors:
            if c.player1.firstname == PlayerData.lele.firstname:
                self.assertIsNone(c.idplayer2)
            elif c.player1.firstname == PlayerData.bob.firstname:
                self.assertEqual(c.player2.firstname, PlayerData.fata.firstname)


class TestSerialization(TestCase):
    def test_sol_loader(self):
        from os.path import join, split
        from sol.models.bio import load_sol
        from sol.models import DBSession
        from sol.models.errors import LoadError

        s = DBSession()

        fullname = join(split(__file__)[0], 'scr',
                        'Campionato_SCR_2007_2008.sol.gz')
        try:
            tourneys = load_sol(s, fullname)
        except LoadError as e:
            self.assertIn('already present', e.message)

        fullname = join(split(__file__)[0], 'scr',
                        'Campionato_SCR_2008_2009.sol')

        tourneys = load_sol(s, fullname)

        self.assertEqual(tourneys[0].championship.previous.description,
                         'Campionato SCR 2007-2008')

        lele, = [c.player1 for c in tourneys[0].competitors
                 if c.player1.nickname == 'Lele']
        self.assertEqual(lele.firstname, 'Emanuele')
        self.assertEqual(lele.lastname, 'Gaifas')
        self.assertEqual(lele.portrait, 'lele.png')

    def test_full_dump_load(self):
        from os.path import join, split
        from sol.models.bio import load_sol
        from sol.models import DBSession

        s = DBSession()

        fullname = join(split(__file__)[0], 'scr', 'dump.sol.gz')
        tourneys = load_sol(s, fullname)
        onechampionship = tourneys[0].championship
        for t in tourneys:
            if t.championship is not onechampionship:
                otherchampionship = t.championship
                break
        if onechampionship.previous:
            self.assertEqual(onechampionship.previous.description,
                             otherchampionship.description)
        else:
            self.assertEqual(otherchampionship.previous.description,
                             onechampionship.description)

    def test_full_dump_reload(self):
        from io import StringIO

        from sol.models.bio import dump_sol, load_sol
        from sol.models import DBSession, Player, Tourney, wipe_database
        from . import PlayerData, RatingData, TourneyData

        s = DBSession()

        tourneys = s.query(Tourney).all()
        ntourneys = len(tourneys)

        dump = dump_sol(tourneys, False)

        wipe_database()

        s.expunge_all()

        load_sol(s, 'dump.sol', StringIO(dump))
        tourneys = s.query(Tourney).all()
        newntourneys = len(tourneys)

        self.assertEqual(ntourneys, newntourneys)

        t = s.query(Tourney).filter_by(
            description=TourneyData.rated.description).one()

        self.assertEqual(t.rating.description, RatingData.national.description)

        fata = PlayerData.fata
        p = s.query(Player).filter_by(lastname=fata.lastname).one()

        self.assertEqual(p.nationality, fata.nationality)
        self.assertEqual(p.language, fata.language)
        self.assertEqual(p.citizenship, fata.citizenship)
        self.assertEqual(p.email, fata.email)

    def test_load_rated_tourney(self):
        from os.path import join, split
        from sol.models.bio import load_sol
        from sol.models import DBSession

        s = DBSession()

        fullname = join(split(__file__)[0], 'scr',
                        'Campionato_SCR_1999_2000-2000-10-21+6.sol')
        tourneys = load_sol(s, fullname)

        self.assertEqual(tourneys[0].rating.description,
                         'Test')
        self.assertEqual(len(tourneys[0].rating.rates), 21)


class TestBackup(TestCase):
    def test_full_backup_restore(self):
        from io import BytesIO
        from sol.models.bio import backup, restore
        from sol.models import DBSession, Rate, Tourney, wipe_database

        s = DBSession()
        tourneysc = len(s.query(Tourney).all())
        archive = backup(s, '/tmp', '/tmp')
        wipe_database()
        s.expunge_all()
        tourneys = restore(s, content=BytesIO(archive))
        self.assertEqual(len(tourneys), tourneysc)

        # Our test data isn't completely consistent, as we have player ratings
        # that does not have a corresponding tourney: when we reload everything,
        # the ratings gets recomputed from scratch, so we cannot compare the
        # number of current player ratings with the previous one.
        rates = s.query(Rate).all()
        self.assertEqual(len(rates), 12)


class TestReplay(TestCase):
    def test_update_incomplete_tourney(self):
        from datetime import date, timedelta
        from io import StringIO
        from sol.models.bio import dump_sol, load_sol
        from sol.models import DBSession, Competitor, Player, Tourney
        from . import TourneyData

        s = DBSession()
        t = s.query(Tourney).filter_by(
            description=TourneyData.first.description).one()
        n = t.replay(date.today()+timedelta(days=1))
        s.flush()
        dump = dump_sol([n])
        newguy = Player(firstname='New', lastname=u'Guy')
        n.competitors.append(Competitor(player1=newguy))
        s.flush()
        load_sol(s, 'dump.sol', StringIO(dump))
        s.flush()

        s = DBSession()
        reloaded = s.query(Tourney).get(n.idtourney)
        self.assertNotIn(newguy, reloaded.allPlayers())


class TestMerge(TestCase):
    def test_merge(self):
        from os.path import join, split
        from sol.models.bio import load_sol
        from sol.models import DBSession, Player

        s = DBSession()

        fullname = join(split(__file__)[0], 'scr',
                        'Lazio_2011_2012-2012-01-29+6.sol')
        load_sol(s, fullname)

        fullname = join(split(__file__)[0], 'scr',
                        'Single_Event-2013-06-22+11.sol')
        load_sol(s, fullname)

        elene = s.query(Player).filter_by(firstname='Lucia Elene').one()
        elena = s.query(Player).filter_by(firstname='Lucia Elena').one()

        elena_id = elena.idplayer
        elena_guid = elena.guid

        elene_guid = elene.guid
        elena.mergePlayers([elene_guid])

        s.flush()
        transaction.commit()
        s.expunge_all()

        elena = s.query(Player).get(elena_id)
        self.assertIn(elene_guid, set(m.guid for m in elena.merged))

        self.assertRaises(NoResultFound,
                          s.query(Player).filter_by(firstname='Lucia Elene').one)

        fullname = join(split(__file__)[0], 'scr',
                        'Double_Event-2013-06-19+7.sol')
        load_sol(s, fullname)

        s.flush()
        transaction.commit()
        s.expunge_all()

        self.assertRaises(NoResultFound,
                          s.query(Player).filter_by(firstname='Lucia Elene').one)

        from io import BytesIO
        from sol.models.bio import backup, restore
        from sol.models import wipe_database

        archive = backup(s, '/tmp', '/tmp')
        wipe_database()
        s.expunge_all()
        restore(s, content=BytesIO(archive))
        elena = s.query(Player).filter_by(guid=elena_guid).one()
        self.assertIn(elene_guid, set(m.guid for m in elena.merged))


class TestMerged(TestCase):
    def test_merge(self):
        from os.path import join, split
        from sol.models.bio import load_sol
        from sol.models import DBSession, Player

        s = DBSession()

        fullname = join(split(__file__)[0], 'scr',
                        'Lazio_2011_2012-2012-01-29+6.sol')
        load_sol(s, fullname)

        fullname = join(split(__file__)[0], 'scr',
                        'Single_Event-2013-06-22+11.sol')
        load_sol(s, fullname)

        elena = s.query(Player).filter_by(firstname='Lucia Elena').one()
        elene = s.query(Player).filter_by(firstname='Lucia Elene').one()

        elena_id = elena.idplayer
        elene_guid = elene.guid

        fullname = join(split(__file__)[0], 'scr',
                        'Lazio_2011_2012-2012-03-18+6.sol')
        load_sol(s, fullname)

        s.flush()
        transaction.commit()
        s.expunge_all()

        elena = s.query(Player).get(elena_id)
        self.assertIn(elene_guid, set(m.guid for m in elena.merged))

        self.assertRaises(NoResultFound,
                          s.query(Player).filter_by(guid=elene_guid).one)
