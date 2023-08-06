# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    lun 16 dic 2013 20:14:45 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from . import AuthenticatedTestCase


class TestSvgController(AuthenticatedTestCase):

    def test_rating(self):
        from .. import RatingData

        response = self.app.get('/data/ratings')
        result = response.json
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], "Ok")
        self.assertEqual(result['root'][0]['description'],
                         RatingData.european.description)

        idrating = result['root'][0]['idrating']

        response = self.app.get('/data/ratedPlayers?filter_idrating=%d' % idrating)
        result = response.json

        p1 = result['root'][0]['idplayer']
        p2 = result['root'][1]['idplayer']
        p3 = result['root'][2]['idplayer']
        p4 = result['root'][3]['idplayer']

        response = self.app.get(('/svg/ratingchart?idrating=%d&player=' % idrating)
                                + '&player='.join(map(str, [p1, p2, p3, p4])))
        self.assert_(response.text.startswith(
            '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<svg'))

    def test_players_distribution(self):
        response = self.app.get('/svg/playersdist')
        self.assert_(response.text.startswith(
            '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<svg'))
