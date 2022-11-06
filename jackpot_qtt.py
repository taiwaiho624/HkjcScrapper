from unittest import result
from core import GenericWebScrapper
from core import GenericUrlGenerator
from core import GenericXmlScrapper
from utils import postgresClient
from utils import logger
from utils import util
import re
import logging

#run once after race_day
class JackpotUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def Generate(self):            
        race_day = util.GetTodayDate()

        url = f'https://iosbsinfo02.hkjc.com/infoA/AOSBS/HR_GetInfo.ashx?QT=HR_ODDS_ALL&Race=*&Venue=*&Result=1&Dividend=1&JTC=1&JKC=1&TNC=1&Lang=zh-HK'

        dynamicFields = {
            "match_id" : race_day,
        }
        
        yield [url, dynamicFields]
            


class JackpotScrapper(GenericXmlScrapper.GenericXmlScrapper):
    def isValid(self, context):
        for info in context.find("Meetings").find("MeetingInfo").find("GeneralInfoSet").findall('GeneralInfo'):
            if info.get("Pool") == "QTT,F-F":
                return True
        return False
            

    def setStaticValues(self):
        pass
        
    def decode(self, context):
        venue = None
        for info in context.find("Meetings"):
            venue = info.get("Venue")

        for info in context.find("Meetings").find("MeetingInfo").find("GeneralInfoSet").findall('GeneralInfo'):
            if info.get("Pool") == "QTT,F-F":
                jackpot = info.get("Jackpot").replace(",","")
                raceNo = info.get("Race")
                self.data["qtt_jackpot"]["value"] = jackpot
                match_id = util.ConstructMatchId(self.data["match_id"]["value"], raceNo, venue)
                self.data["match_id"]["value"] = match_id
                self.writeToDb()
                self.cleanValue()
                self.data["match_id"]["value"] = util.GetTodayDate()

if __name__ == "__main__":
    try: 
        tableName = "jackpot_qtt"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = JackpotScrapper(
            tableName, 
            JackpotUrlGenerator(), 
            postgresClient,
            True,
            customWrite = True
        )

        scapper.Start()
    except Exception as error:
        logging.exception(error)