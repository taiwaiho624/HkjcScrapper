from asyncio import Handle
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
    def __init__(self, fromDate):
        self.fromDate = fromDate 
        super().__init__()
        
    def Generate(self):
        venues = ["ST", "HV"]
        for date in util.DateGenerator(self.fromDate):
            for venue in venues:
                for raceNo in range(6,12):
                    dateNewFormat = datetime.datetime.strptime(date, "%Y/%m/%d")
                    match_id =  dateNewFormat.strftime("%Y%m%d") + str(raceNo).zfill(2) + venue

                    url = "https://racing.hkjc.com/racing/information/english/Racing/LocalResults.aspx?RaceDate=" + date + "&Racecourse=" + venue + "&RaceNo=" + str(raceNo)
                                    
                    dynamicFields = {
                        "match_id" : match_id,
                        'url' : url
                    }
                    
                    yield [url, dynamicFields]     


class ResultAndDividendScrapper(GenericWebScrapper.GenericWebScrapper):
    def isValid(self, context):
        value = context.GetText(self.webData["horse_1_number"]['xpath'])
        if value == None:
            return False

        tbodys = context.Get(self.webData["dividend_table"]["xpath"])
        for tbody in tbodys:
            rowNo= 0
            for row in tbody.xpath("./tr"):
                rowNo = rowNo + 1
                pool = row.xpath("./td")[0]
                heading = pool.text.replace(" ", "").replace("\r\n", "")
                if heading == "SIXUP":
                    return True

        return False

    def HandleSixUp(self, context, rowNo, rawPath):
        try:
            tmp = context.GetText("{}/tr[{}]/td[{}]".format(rawPath, str(rowNo + 1), "1")).replace(",", "|")
        except:
            tmp = "JOCKEY"
   
        if "JOCKEY" not in tmp:
            self.data["sixup_combination_1"]["value"] = context.GetText("{}/tr[{}]/td[{}]".format(rawPath, str(rowNo + 1), "1")).replace(",", "|")
            self.data["sixup_dividend_1"]["value"] = float(context.GetText("{}/tr[{}]/td[{}]".format(rawPath, str(rowNo + 1), "2")).replace(",",""))

            self.data["sixup_combination_2"]["value"] = context.GetText("{}/tr[{}]/td[{}]".format(rawPath, str(rowNo), "2")).replace(",", "|")
            self.data["sixup_dividend_2"]["value"] = float(context.GetText("{}/tr[{}]/td[{}]".format(rawPath, str(rowNo), "3")).replace(",", ""))
        else: 
            self.data["sixup_combination_2"]["value"] = context.GetText("{}/tr[{}]/td[{}]".format(rawPath, str(rowNo), "2")).replace(",", "|")
            self.data["sixup_dividend_2"]["value"] = float(context.GetText("{}/tr[{}]/td[{}]".format(rawPath, str(rowNo), "3")).replace(",", ""))
    
    def decode(self, context):
        rawPath = self.webData["dividend_table"]["xpath"]
        tbodys = context.Get(self.webData["dividend_table"]["xpath"])
        for tbody in tbodys:
            rowNo= 0
            for row in tbody.xpath("./tr"):
                rowNo = rowNo + 1
                pool = row.xpath("./td")[0]
                heading = pool.text.replace(" ", "").replace("\r\n", "")
                if heading == "SIXUP":
                    self.data["match_id"]["value"] = util.MinusDayFromMatchId(self.data["match_id"]["value"], 5)
                    self.HandleSixUp(context, rowNo, rawPath)                    
                    
    
    def setStaticValues(self):
        self.data["data_source"]['value'] = "hkjc"
        

if __name__ == "__main__":
    try: 
        tableName = "sixup_result_and_dividend"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        date = None

        if len(sys.argv) == 1:
            date = util.GetTodayDate()
        else:
            date = sys.argv[1]

        scapper = ResultAndDividendScrapper(
            tableName, 
            ResultAndDividendUrlGenerator(date), 
            postgresClient,
            True
        )

        scapper.Start()
        
    except Exception as error:
        logging.exception(error)