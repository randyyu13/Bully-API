from playwright.sync_api import sync_playwright
import re
from cloudsql_server_broker import cloudsql_server_broker
import os
from enums import Site, Sport
from datetime import datetime

#TODO make map from how covers displays each stat to the stat name I want to actually put into the db

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
        self.__standardize_covers_NBA_player_prop_names = {
            'Points Scored' : 'Points',
            'Points and Rebounds' : 'Points + Rebounds',
            'Points and Assists': 'Points + Assists',
            '3 Pointers Made' : '3 Pointers Made',
            'Rebounds and Assists' : 'Rebounds + Assists',
            'Record a Double Double' : 'Double Double',
            'Record a Triple Double' : 'Triple Double',
            'Score First Field Goal' : 'First Field Goal',
            'Steals and Blocks' : 'Steals + Blocks',
            'Total Blocks': 'Blocks',
            'Total Steals' : 'Steals',
            'Total Rebounds' : 'Rebounds',
            'Total Points, Rebounds, and Assists' : 'Points + Rebounds + Assists',
            'Total Turnovers' : 'Turnovers',
            'Total Assists' : 'Assists'
            }
        self.__cloudsql_broker = cloudsql_broker

    def scrape_data(self, site: Site, sport: Sport):
        match site:
            case Site.COVERS:
                self.__scrape_data_from_covers(sport)
            case _:
                return

    def __scrape_data_from_covers(self, sport: Sport):
        match sport:
            case Sport.NBA:
                self.__scrape_NBA_data_from_covers()
            case _:
                return

    '''
    All helper methods
    '''
    def __scrape_NBA_data_from_covers(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto('https://www.covers.com/sport/basketball/nba/player-props')

            matchups = page.query_selector_all('.props-matchup-list-item')
            number_of_matchups = len(matchups)
            
            i = 0
            player_prop_set = set()
            while i < number_of_matchups:
                player_props = page.query_selector_all('.player-prop-article')[1:]
                for prop in player_props:
                    player_link_element = prop.query_selector('.player-link')
                    player_name = player_link_element.text_content()
                    player_link = player_link_element.get_attribute('href')
                    if player_name not in player_prop_set:
                        player_prop_set.add(player_name)
                        player_prop_map = self.__populate_NBA_player_props(player_link, browser)
                        self.__upload_props_to_db(player_prop_map)
                page.query_selector('#props-event-btn').click()

                i += 1
                matchups[i].click()

                page.wait_for_load_state("networkidle")
        
    def __populate_NBA_player_props(self, player_link, browser):
        print(f'https://www.covers.com{player_link}')
        page = browser.new_page()
        page.goto(f'https://www.covers.com{player_link}')
        try:
            page.wait_for_selector('.covers-CoversPlayer-Prop-Event')
        except:
            print("timed out waiting for cards")
            return {}
        all_cards = page.query_selector_all('.covers-CoversPlayer-Prop-Event')
        expanded_player_name = ' '.join(page.query_selector("h1").text_content().split()[:-4])
        print(expanded_player_name)
        prop_data_map = {}
        for card in all_cards:
            button = card.query_selector('text="Compare odds"')
            button.click()
            
            rows = card.query_selector_all('.other-odds-row')
            all_sb_odds_rows = rows[2:]

            current_stat = card.query_selector("h2").text_content()[:-5]

            for row in all_sb_odds_rows:
                num_cols_in_row = len(row.query_selector_all('div'))
                sportsbook_img_src = row.query_selector('img').get_attribute('src')
                sportsbook_name = self.__covers_image_link_to_sportsbook[sportsbook_img_src]
                if num_cols_in_row == 3:
                    # this is the over under for other sportsbook for the stat, this is the data we want for the api.
                    over_line_and_odds = row.query_selector('.other-over-odds').text_content().split()
                    line = float(over_line_and_odds[0][1:])
                    over_odds = eval(re.sub(r',', '', over_line_and_odds[1]))
                    under_line_and_odds = row.query_selector('.other-under-odds').text_content().split()
                    under_odds = eval(re.sub(r',', '', under_line_and_odds[1]))
                    stat_odds_for_different_sportbooks = {'line': line,
                                                        'oOdds': over_odds,
                                                        'uOdds': under_odds}

                else:
                    odds_str = row.query_selector('.other-over-odds').text_content().split()[0]
                    odds_without_commas = re.sub(r',', '', odds_str)
                    parsed_odds = eval(odds_without_commas)
                    stat_odds_for_different_sportbooks = {'line': 0.5,
                                                        'oOdds': parsed_odds,
                                                        'uOdds': None}
                
                
                if current_stat not in prop_data_map:
                    prop_data_map[current_stat] = {}
                prop_data_map[current_stat][sportsbook_name] = stat_odds_for_different_sportbooks

        player_props_map = {}
        player_props_map[expanded_player_name] = prop_data_map
        return player_props_map
    
    def __upload_props_to_db(self, player_props_map):
        for player in player_props_map:
            for prop_type in player_props_map[player]:
                for sb in player_props_map[player][prop_type]:
                    sb_data = player_props_map[player][prop_type][sb]

                    line = None
                    over_odds = None
                    under_odds = None

                    line = sb_data['line']
                    over_odds = sb_data['oOdds']
                    under_odds = sb_data['uOdds']
                    print((player, prop_type, sb, line, over_odds, under_odds, datetime.now()))
                    standardized_prop_type = self.__standardize_covers_NBA_player_prop_names[prop_type]
                    self.__cloudsql_broker.write_to_player_prop_table(player, standardized_prop_type, sb, line, over_odds, under_odds, datetime.now())