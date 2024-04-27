import requests
from playwright.sync_api import sync_playwright
import os

sportbook_links = {
    'bet365' : 'https://www.la.bet365.com/',
    'draftkings' : 'https://sportsbook.draftkings.com/',
    'fanduel' : 'https://sportsbook.fanduel.com/',
    'betmgm' : 'https://sports.ny.betmgm.com/en/',
    'espnbet' : 'https://espnbet.com/',
    'betrivers' : 'https://pa.betrivers.com/?page=sportsbook',
    'partycasino' : 'https://sports.partycasino.com/en-ca/sports'
}

class sportbook_scraper:
    def __init__(self):
        self.__sportsbooks = [
            self.sportsbook('bet365'),
            self.sportsbook('betmgm'),
            self.sportsbook('betrivers'),
            self.sportsbook('draftkings'),
            self.sportsbook('espnbet'),
            self.sportsbook('fanduel'),
            self.sportsbook('partycasino')
        ]
    
    def scrape_books(self):
        return

    class sportsbook:
        def __init__(self, sportsbook_name):
            self.__sportsbook_name = sportsbook_name
            self.__sportsbook_url = sportbook_links[sportsbook_name]

        def get_name(self):
            return self.__sportsbook_name 
        
        def get_url(self):
            return self.__sportsbook_url
        
    def scrape_player_props(self, sb: sportsbook):
        match sb.get_name():
            case 'bet365':
                self.__player_props_bet365(sb)
            case 'betmgm':
                self.__player_props_betmgm(sb)
            case 'betrivers':
                self.__player_props_betrivers(sb)
            case 'draftkings':
                self.__player_props_draftkings(sb)
            case 'espnbet':
                self.__player_props_espnbet(sb)
            case 'fanduel':
                self.__player_props_fanduel(sb)
            case 'partycasino':
                self.__player_props_partycasino(sb)
            case _:
                self.__player_props_bet365(sb)
        return None

    def __player_props_bet365(book: sportsbook):
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.getenv('CHROMIUM_EXECUTABLE_PATH'))
            page = browser.new_page()
            page.goto(book.get_url())

            page.wait_for_load_state('networkidle')

            button = page.locator('.wn-PreMatchItem:has-text("NBA")')
            button.click()

            page.wait_for_load_state("networkidle")

            all_games = page.query_selector_all('.ParticipantFixtureDetailsHigherBasketball_LhsContainerInner')
            
            for game in all_games:
                if(game.query_selector('.pi-CouponParticipantClockInPlay_Extra')):
                    continue
                game.click()
                page.wait_for_load_state('networkidle')

                player_parlays = page.locator('.bmp-TabButton.bmp-TabButton-7:has-text("Player")')



            
        return
    
    def __player_props_betmgm(book):
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.getenv("CHROMIUM_EXECUTABLE_PATH"))
            page = browser.new_page()
            page.goto(book.get_url())
        return
    
    def __player_props_betrivers(book):
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.getenv("CHROMIUM_EXECUTABLE_PATH"))
            page = browser.new_page()
            page.goto(book.get_url())
        return
    
    def __player_props_draftkings(book):
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.getenv("CHROMIUM_EXECUTABLE_PATH"))
            page = browser.new_page()
            page.goto(book.get_url())
        return
    
    def __player_props_espnbet(book):
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.getenv("CHROMIUM_EXECUTABLE_PATH"))
            page = browser.new_page()
            page.goto(book.get_url())
        return
    
    def __player_props_fanduel(book):
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.getenv("CHROMIUM_EXECUTABLE_PATH"))
            page = browser.new_page()
            page.goto(book.get_url())
        return
    
    def __player_props_partycasino(book):
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.getenv("CHROMIUM_EXECUTABLE_PATH"))
            page = browser.new_page()
            page.goto(book.get_url())
        return