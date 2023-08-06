from champions import ChampionsApi
from data import StaticDataApi
from games import GamesApi
from leagues import LeaguesApi
from stats import StatsApi
from summoners import SummonersApi
from teams import TeamsApi

from exceptions import UnsupportedRegion

class LolApi(object):

    def __init__(self, region, key):    	
        self.set_region(region)
    	self.key = key

    	# setup resources
    	self.champions = ChampionsApi(self)
        self.games = GamesApi(self)
        self.summoners = SummonersApi(self)
        self.teams = TeamsApi(self)
        self.leagues = LeaguesApi(self)
        self.stats = StatsApi(self)
        self.data = StaticDataApi(self)

    def set_region(self, region):
        if region not in ['br', 'eune', 'euw', 'lan', 'las', 'na', 'oce', 'ru']:
            raise UnsupportedRegion()
        self.region = region