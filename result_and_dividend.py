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

class ResultAndDividendUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def __init__(self, date):
        super().__init__()
        self.fromDate = date 
        
    def Generate(self):
        venues = ["ST", "HV"]
        for date in util.DateGenerator(self.fromDate):
            for venue in venues:
                for race_no in range(1,12):
                    if self.isValid == False:
                        self.isValid = True
                        break
                    
                    url = "https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=" + date + "&Racecourse=" + venue + "&RaceNo=" + str(race_no)
                    dynamicFields = {
                        "match_id" : util.ConstructMatchId(date, race_no, venue),
                        "url" : url
                    }
                    
                    yield [url, dynamicFields]
                 


class ResultAndDividendScrapper(GenericWebScrapper.GenericWebScrapper):
    def __init__(self, tableName, urlGenerator, postgresClient, isUpsert=False, duplicateChecker=None, customWrite=False, onlyRunOnRaceDay=True):
        super().__init__(tableName, urlGenerator, postgresClient, isUpsert, duplicateChecker, customWrite, onlyRunOnRaceDay)
    
    def writeDhToFile(self):
        file = open("data/result_and_dividend_same_rank_list.txt", "a")
        file.write(self.data["url"]["value"] + "\n")

    def isValid(self, context):
        value = context.GetText(self.webData["rank_1_horse_number"]['xpath'])
        if value == None:
            return False 
        return True

    def decode(self, context):
        isSameRankUrl = False
        dhMap = {}
        i = 1
        j = 1
        for key in self.webData.keys():
            value = context.GetText(self.webData[key]["xpath"])
            if "left" in key:
                if value != None and "DH" in value:
                    isSameRankUrl = True
                    dhMap[i] = str(value[:-2]).replace(" ", "")
                else:
                    dhMap[i] = str(i)
                i += 1
            else:
                if value != None:
                    value = value.replace("\r\n", "").replace(" ", "")
                    
                    #not same rank
                    if dhMap[j] == str(j):
                        self.data[key]["value"] = value
                    #if same rank
                    else: 
                        key = dhMap[j].replace(u'\xa0', u' ').replace(" ","")
                        if self.data[f'rank_{key}_horse_number']["value"] == "N/A":
                           self.data[f'rank_{key}_horse_number']["value"] = ""
                        
                        if len(self.data[f'rank_{key}_horse_number']["value"]) == 0:
                            self.data[f'rank_{key}_horse_number']["value"] += f"{value}"
                        else:
                            self.data[f'rank_{key}_horse_number']["value"] += f"/{value}"
                j += 1

        if isSameRankUrl:
            self.writeDhToFile()

    def setStaticValues(self):
        self.data["data_source"]['value'] = "hkjc"



if __name__ == "__main__":
    try: 
        tableName = "result_and_dividend"
        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        date = None

        onlyRunOnRaceDay = False

        if len(sys.argv) == 1:
            onlyRunOnRaceDay = True 
            date = util.GetTodayDate()
        else:
            date = sys.argv[1]


        scapper = ResultAndDividendScrapper(
            tableName, 
            ResultAndDividendUrlGenerator(date), 
            postgresClient,
            onlyRunOnRaceDay=onlyRunOnRaceDay
        )

        scapper.Start()
        
    except Exception as error:
        logging.exception(error) 