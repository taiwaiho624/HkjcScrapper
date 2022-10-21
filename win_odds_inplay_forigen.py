from curses.ascii import isdigit
from shutil import ExecError
from unittest import result
from core import GenericWebScrapper
from core import GenericUrlGenerator
from core import DuplicateChecker
from utils import postgresClient
from utils import logger
from utils import util
from utils import request
import time 
import logging
import datetime
import sys 
import requests

class WinOddsForigenUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def GetUrls(self):
        session = requests.Session()
        headers = {'Cookie': 'rmbs=3; aps03=cf=N&cg=2&cst=0&ct=42&hd=N&lng=10&oty=2&tzi=27; session=processform=0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'}
        result = session.get("https://www.bet365.com/#/AS/B2/", headers=headers)
        print(result)

    def Generate(self):
        self.GetUrls()

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