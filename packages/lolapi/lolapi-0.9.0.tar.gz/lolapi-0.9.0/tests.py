#!/usr/bin/env python
try:
    import _keys
except ImportError:
    pass

import unittest
import lolapi

class TestLolApi(unittest.TestCase):

    def setUp(self):
        self.api = lolapi.LolApi(region='na', key=_keys.API_KEY)
        self.sum_name = u'meteos'
        self.sum_id = u'44008519'

    def test_champions_api(self):
        data = self.api.champions.get_all()
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['champions'], list)
        self.assertIsInstance(data['champions'][0], dict)
        self.assertTrue(len(data['champions']) > 100)

    def test_games_api(self):
        data = self.api.games.get_recent(self.sum_id)

    def test_leagues_api(self):
        pass

    def test_data_api(self):
        pass

    def test_stats_api(self):
        pass

    def test_summoners_api(self):
        pass

    def test_teams_api(self):
        pass

if __name__ == '__main__':
    if _keys.API_KEY:
        unittest.main()