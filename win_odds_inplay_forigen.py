from curses.ascii import isdigit
from shutil import ExecError
from unittest import result
from core import GenericWebScrapper
from core import GenericUrlGenerator
from core import DuplicateChecker
from utils import postgresClient
from utils import logger
from utils import util
import time 
import logging
import datetime
import sys 
import requests

class WinOddsForigenUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def Generate(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
                    'referer': "https://www.oddschecker.com/",
                    'origin': "https://www.oddschecker.com"}
        print(requests.get("https://www.oddschecker.com/horse-racing/sha-tin/06:00/winner", headers=headers).content)
        yield ["https://www.oddschecker.com/horse-racing/sha-tin/06:00/winner", {}]

class WinOddsForigenScrapper(GenericWebScrapper.GenericWebScrapper):
    def isValid(self, context):
        return True

    def setStaticValues(self):
        self.data["status"]['value'] = 1 
        self.data["data_source"]['value'] = "oddsChecker"
        
    def decode(self, context):
        print(context.GetAlt(self.webData["dealer_1_name"]["value"]))

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