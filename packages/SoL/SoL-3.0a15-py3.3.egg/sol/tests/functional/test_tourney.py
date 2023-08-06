# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    gio 23 ott 2008 11:16:12 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from . import AuthenticatedTestCase


class TestTourneyController(AuthenticatedTestCase):
    def setUp(self):
        from ...models import DBSession, Tourney
        from ..data import TourneyData

        s = DBSession()
        first = s.query(Tourney) \
                .filter_by(description=TourneyData.first.description).one()
        self.idtourney = first.idtourney

    def test_competitors(self):
        response = self.app.get('/tourney/competitors?filter_idtourney=%d'
                                % self.idtourney)
        result = response.json
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], "Ok")
        self.assertEqual(result['count'], 6)

    def test_matches(self):
        response = self.app.get('/tourney/matches?filter_idtourney=%d'
                                % self.idtourney)
        result = response.json
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], "Ok")
        self.assertEqual(result['count'], 9)

    def test_ranking(self):
        response = self.app.get('/tourney/updateRanking?idtourney=%d'
                                % self.idtourney)
        result = response.json
        self.assertEqual(result['success'], False)
        self.assertIn('not allowed', result['message'])

    def test_boards(self):
        response = self.app.get('/tourney/boards?filter_idtourney=%d'
                                % self.idtourney)
        result = response.json
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], "Ok")
        self.assertEqual(result['count'], 3)

    def test_clock(self):
        response = self.app.get('/tourney/clock?idtourney=%d'
                                % self.idtourney)
        self.assertIn('CoolAlarmClock', response.text)


class TestRanking(AuthenticatedTestCase):
    USERNAME = 'admin'
    PASSWORD = 'admin'

    def setUp(self):
        from ...models import DBSession, Tourney
        from ..data import TourneyData

        s = DBSession()
        first = s.query(Tourney) \
                .filter_by(description=TourneyData.first.description).one()
        self.idtourney = first.idtourney

    def test_ranking(self):
        response = self.app.get('/tourney/updateRanking?idtourney=%d'
                                % self.idtourney)
        result = response.json
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], "Ok")
        self.assertEqual(result['currentturn'], result['rankedturn'])
        self.assertEqual(result['prized'], False)

        response = self.app.get('/tourney/ranking?filter_idtourney=%d'
                                % self.idtourney)
        result = response.json
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], "Ok")
        self.assertEqual(result['count'], 6)
        self.assertEqual([r['rank'] for r in result['root']],
                         list(range(1, 7)))
        astuples = [(r['prize'], r['points'], r['bucholz'],
                     r['netscore'], r['totscore'], r['rank'])
                    for r in result['root']]
        astuples.sort()
        self.assertEqual([r[5] for r in astuples], list(range(6, 0, -1)))


class TestPrizing(AuthenticatedTestCase):
    USERNAME = 'admin'
    PASSWORD = 'admin'

    def setUp(self):
        from ...models import DBSession, Tourney
        from ..data import TourneyData

        s = DBSession()
        t = s.query(Tourney) \
             .filter_by(description=TourneyData.second.description).one()
        self.idtourney = t.idtourney

    def test_assign_prizes(self):
        from ...models import DBSession, Tourney

        response = self.app.get('/tourney/assignPrizes?idtourney=%d'
                                % self.idtourney)
        result = response.json
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], "Ok")

        s = DBSession()
        t = s.query(Tourney).get(self.idtourney)
        self.assertEqual(t.prized, True)
        self.assertEqual(t.ranking[0].prize, 18)
        return t


class TestRatedPrizing(TestPrizing):
    def setUp(self):
        from ...models import DBSession, Tourney
        from ..data import TourneyData

        s = DBSession()
        first = s.query(Tourney) \
                .filter_by(description=TourneyData.rated.description).one()
        self.idtourney = first.idtourney

    def test_assign_prizes(self):
        t = super().test_assign_prizes()
        self.assertEqual(t.rating.rates[-1].date, t.date)
