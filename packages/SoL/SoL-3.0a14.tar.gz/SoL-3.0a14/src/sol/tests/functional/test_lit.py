# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    sab 13 dic 2008 16:35:46 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from . import FunctionalTestCase


class TestHtmlController(FunctionalTestCase):

    def test_index(self):
        self.app.get('/lit')

    def test_championshipranking(self):
        self.app.get('/lit/championshipranking?idchampionship=1')

    def test_tourney(self):
        self.app.get('/lit/tourney?idtourney=1')

    def test_player(self):
        self.app.get('/lit/player?idplayer=1')

    def test_emblem(self):
        from webtest.app import AppError

        response = self.app.get('/lit/emblem/emblem.png')
        assert response.headers['content-type'].startswith('image')

        try:
            self.app.get('/lit/emblem')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

        try:
            self.app.get('/lit/emblem/foo')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

    def test_portrait(self):
        from webtest.app import AppError

        response = self.app.get('/lit/portrait/portrait.png')
        assert response.headers['content-type'].startswith('image')

        try:
            self.app.get('/lit/portrait'),
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

        try:
            self.app.get('/lit/portrait/foo')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"
