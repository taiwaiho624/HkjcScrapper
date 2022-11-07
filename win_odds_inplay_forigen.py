from curses.ascii import isdigit
from shutil import ExecError
from unittest import result
from core import GenericWebScrapper
from core import GenericUrlGenerator
from core import GenericSeleniumScrapper
from core import DuplicateChecker
from utils import postgresClient
from utils import logger
from utils import util
from utils import request
from utils import selenium_request
import time 
import logging
import datetime
import sys 
import requests

venues = {
    "sha-tin" : "ST",
    "happy-valley" : "HV",
    "Morioka" : "MK"
} 

dealer_name = {
    "SK" : {
        "name"  : "Sky Sports",
        "index" : 2
    },
    "B3" : {
        "name"  : "Bet365",
        "index" : 1
    },
}


class WinOddsForigenUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def GetUrls(self):
        self.urls = []
        self.venue = ""
        r = selenium_request.Request("https://www.oddschecker.com/horse-racing")
        for matchDiv in r.find_all("div", {"class" : "race-details"}):
            venue = matchDiv.find_all("a")[0].text
            if venue in venues:
                self.venue = venues[venue] 
                for matchUrl in matchDiv.find_all("div", {"class" : "all-todays-races"})[0].find_all("a"):
                    self.urls.append("https://www.oddschecker.com" + matchUrl["href"])
                    
                break

    def Generate(self):
        self.GetUrls()

        race_day = util.GetTodayDate()

        while True:
            for i, url in enumerate(self.urls):
                dynamicFields = {
                    "match_id" : util.ConstructMatchId(race_day, i + 1, self.venue)
                }

                yield [url, dynamicFields]

            time.sleep(10)

class WinOddsForigenScrapper(GenericSeleniumScrapper.GenericSeleniumScrapper):
    def isValid(self, context):
        return True

    def setStaticValues(self):
        self.data["status"]['value'] = 1 
        self.data["data_source"]['value'] = "oddsChecker"
        
    def decode(self, context):
        for row in context.find_all("tbody", {"id" : "t1"})[0].find_all("tr", {"class" : "diff-row"}):
            horse_number = row.find_all("td", {"class" : "cardnum"})[0].text
            
            for odd in row.find_all("td"):
                if odd.get("data-bk") in dealer_name and odd.text != "":
                    dealer_index = dealer_name[odd["data-bk"]]["index"]
                    self.data["dealer_{}_name".format(dealer_index)]["value"] = dealer_name[odd["data-bk"]]["name"]
                    self.data["dealer_{}_horse_{}_odds".format(dealer_index, horse_number)]["value"] = odd["data-odig"]

if __name__ == "__main__":
    try:
        tableName = "win_odds_inplay_forigen"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = WinOddsForigenScrapper(
            tableName, 
            WinOddsForigenUrlGenerator(), 
            postgresClient
        )

        scapper.Start()

    except Exception as error:
        logging.exception(error)