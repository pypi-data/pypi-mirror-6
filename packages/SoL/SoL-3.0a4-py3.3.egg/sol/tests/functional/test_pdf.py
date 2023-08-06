# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    ven 31 ott 2008 16:56:00 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from . import FunctionalTestCase


class TestPdfController(FunctionalTestCase):

    def test_participants(self):
        self.app.get('/pdf/participants?idtourney=1')

    def test_ranking(self):
        self.app.get('/pdf/ranking?idtourney=1')

    def test_nationalranking(self):
        self.app.get('/pdf/nationalranking?idtourney=1')

    def test_results(self):
        self.app.get('/pdf/results?idtourney=1')

    def test_matches(self):
        self.app.get('/pdf/matches?idtourney=1')

    def test_scorecards(self):
        self.app.get('/pdf/scorecards?idtourney=1')

    def test_blank_scorecards(self):
        self.app.get('/pdf/scorecards')

    def test_badges(self):
        self.app.get('/pdf/badges?idtourney=1')

    def test_championshipranking(self):
        self.app.get('/pdf/championshipranking?idchampionship=1')

    def test_ratingranking(self):
        self.app.get('/pdf/ratingranking?idrating=1')
