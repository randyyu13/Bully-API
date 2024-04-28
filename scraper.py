from playwright.sync_api import sync_playwright
import re
import cloudsql_server_broker
import os
from enums import Site, Sport

class scraper:
    def __init__(self, cloudsql_broker: cloudsql_server_broker):
        self.__covers_image_link_to_sportsbook = {
            'https://img.covers.com/covers/data/sportsbooks/pointsbet.svg' : 'PointsBet',
            'https://img.covers.com/covers/data/sportsbooks/draftkings.svg' : 'DraftKings',
            'https://img.covers.com/covers/data/sportsbooks/bet365.svg': 'Bet365',
            'https://img.covers.com/covers/data/sportsbooks/fanduel.svg' : 'FanDuel',
            'https://img.covers.com/covers/data/sportsbooks/betmgm.svg' : 'BetMGM',
            'https://img.covers.com/covers/data/sportsbooks/caesars.svg' : 'Caesars',
            'https://img.covers.com/covers/data/sportsbooks/bet_rivers_co.svg' : 'BetRivers'
            }
        self.__cloudsql_broker = cloudsql_broker

    def scrape_data(self, site: Site, sport: Sport):
        match site:
            case Site.COVERS:
                self.__scrape_data_from_covers(self, sport=sport)
            case _:
                return

    def __scrape_data_from_covers(self, sport: Sport):
        match sport:
            case Sport.NBA:
                self.__scrape_NBA_data_from_covers()
            case _:
                return

    def __scrape_NBA_data_from_covers(self):
        