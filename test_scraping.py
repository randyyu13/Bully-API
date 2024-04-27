from playwright.sync_api import sync_playwright
import re

image_link_to_sportsbook = {
    'https://img.covers.com/covers/data/sportsbooks/pointsbet.svg' : 'PointsBet',
    'https://img.covers.com/covers/data/sportsbooks/draftkings.svg' : 'DraftKings',
    'https://img.covers.com/covers/data/sportsbooks/bet365.svg': 'Bet365',
    'https://img.covers.com/covers/data/sportsbooks/fanduel.svg' : 'FanDuel',
    'https://img.covers.com/covers/data/sportsbooks/betmgm.svg' : 'BetMGM',
    'https://img.covers.com/covers/data/sportsbooks/caesars.svg' : 'Caesars',
    'https://img.covers.com/covers/data/sportsbooks/bet_rivers_co.svg' : 'BetRivers'
    }

def populate_player_props(player_link, player_props_map, player_name, browser):
    print(f'https://www.covers.com{player_link}')
    page = browser.new_page()
    page.goto(f'https://www.covers.com{player_link}')
    try:
        page.wait_for_selector('.covers-CoversPlayer-Prop-Event')
    except:
        print("timed out waiting for cards")
        return
    all_cards = page.query_selector_all('.covers-CoversPlayer-Prop-Event')
    expanded_player_name = ' '.join(page.query_selector("h1").text_content().split()[:-4])
    print(expanded_player_name)
    prop_data_map = {}
    for card in all_cards:
        button = card.query_selector('text="Compare odds"')
        button.click()
        
        page.wait_for_load_state('networkidle')
        rows = card.query_selector_all('.other-odds-row')
        all_sb_odds_rows = rows[2:]

        current_stat = card.query_selector("h2").text_content()[:-5]

        for row in all_sb_odds_rows:
            num_cols_in_row = len(row.query_selector_all('div'))
            sportsbook_img_src = row.query_selector('img').get_attribute('src')
            sportsbook_name = image_link_to_sportsbook[sportsbook_img_src]
            if num_cols_in_row == 3:
                # this is the over under for other sportsbook for the stat, this is the data we want for the api.
                over_line_and_odds = row.query_selector('.other-over-odds').text_content().split()
                over_line = float(over_line_and_odds[0][1:])
                over_odds = eval(over_line_and_odds[1])
                under_line_and_odds = row.query_selector('.other-under-odds').text_content().split()
                under_line = float(over_line_and_odds[0][1:])
                under_odds = eval(under_line_and_odds[1])
                stat_odds_for_different_sportbooks = {'oLine': over_line,
                                                    'uLine': under_line,
                                                    'oOdds': over_odds,
                                                    'uOdds': under_odds}

            else:
                odds_str = row.query_selector('.other-over-odds').text_content().split()[0]
                odds_without_commas = re.sub(r',', '', odds_str)
                parsed_odds = eval(odds_without_commas)
                stat_odds_for_different_sportbooks = {'odds': parsed_odds}
            
            
            if current_stat not in prop_data_map:
                prop_data_map[current_stat] = {}
            prop_data_map[current_stat][sportsbook_name] = stat_odds_for_different_sportbooks
    
    player_props_map[player_name] = {}
    player_props_map[player_name][expanded_player_name] = prop_data_map
    print(player_props_map)
    print('\n')

def update_db():
    iterate_all_props()
    return

def iterate_all_props():
    with sync_playwright() as p:
        print('here')
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('https://www.covers.com/sport/basketball/nba/player-props')

        matchups = page.query_selector_all('.props-matchup-list-item')

        number_of_matchups = len(matchups)
        print(number_of_matchups)
        i = 0

        player_prop_map = {}
        while i < number_of_matchups:
            player_props = page.query_selector_all('.player-prop-article')[1:]
            for prop in player_props:
                player_link_element = prop.query_selector('.player-link')
                player_name = player_link_element.text_content()
                player_link = player_link_element.get_attribute('href')
                if player_name not in player_prop_map:
                    populate_player_props(player_link, player_prop_map, player_name, browser)
            i += 1
            matchups[i].click()
            page.wait_for_load_state("networkidle")

update_db()