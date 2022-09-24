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

class WinOddsUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def __init__(self):
        super().__init__()
        
    def Generate(self):
        venues = ["ST", "HV"]

        race_day = util.GetTodayDate()

        for venue in venues:
            for race_no in range(1,12):
                if self.isValid == False:
                    self.isValid = True
                    break
                
                dynamicFields = {
                    "match_id" : util.ConstructMatchId(race_day, race_no, venue),
                }
                
                yield ["https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx?RaceDate=" + race_day + "&Racecourse=" + venue + "&RaceNo=" + str(race_no), dynamicFields]     


class WinOddsScrapper(GenericWebScrapper.GenericWebScrapper):
    def isValid(self, context):
        value = context.GetText(self.webData["horse_1_number"]['xpath'])
        if value == None or value == '-':
            return False 
        return True

    def decode(self, context):
        for key in self.webData.keys():
            value = context.GetText(self.webData[key]["xpath"])
            if  value != None:
                value = value.replace("\r\n", "").replace(" ", "")
                if value == "":
                    self.webData[key]["value"] = "quit"
                    continue
                
                if "number" in key:
                    self.webData[key]["value"] = value
                else:
                    horseIndex = str([int(s) for s in key.split('_') if s.isdigit()][0])        
                    if self.webData["horse_" + horseIndex + "_number"]["value"] == "N/A":
                        continue
                    
                    if value == "---" or value == "-":
                        value = -1
                    
                    if self.webData["horse_" + horseIndex + "_number"]["value"] != "quit":
                        self.webData["horse_" + self.webData["horse_" + horseIndex + "_number"]["value"]  + "_odds"]["value"] = value
            else:
                self.webData[key]["value"] = "N/A"
                
        for key in self.webData.keys():
            if "number" in key and  self.webData[key]["value"] != "N/A":
                horseNunmber = self.webData[key]['value']
                if horseNunmber != 'quit':
                    self.data["horse_" + horseNunmber + "_odds"]["value"] = self.webData["horse_" + horseNunmber + "_odds"]['value']
    
    
    def setStaticValues(self):
        self.data["status"]['value'] = 2 
        self.data["data_source"]['value'] = "hkjc"
            


if __name__ == "__main__":
    try: 
        print("hi")
        tableName = "win_odds_history"
        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = WinOddsScrapper(
            tableName, 
            WinOddsUrlGenerator(), 
            postgresClient
        )

        scapper.Start()
        
    except Exception as error:
        logging.exception(error) 