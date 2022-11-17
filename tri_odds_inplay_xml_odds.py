from unittest import result
from core import GenericWebScrapper
from core import GenericUrlGenerator
from core import GenericXmlScrapper
from utils import postgresClient
from utils import logger
from utils import util
import re
import logging
import time

class XmlUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def Generate(self):
        self.venue = None

        url = f'https://iosbsinfo02.hkjc.com/infoA/AOSBS/HR_GetInfo.ashx?QT=HR_ODDS_ALL&Race=*&Venue=*&Result=1&Dividend=1&JTC=1&JKC=1&TNC=1&Lang=zh-HK'

        dynamicFields = {}
        while True:
            yield [url, dynamicFields]
            time.sleep(5)
            


class XmlScrapper(GenericXmlScrapper.GenericXmlScrapper):
    def isValid(self, context):
        for info in context.find("Meetings"):
            self.venue = info.get("Venue")

        for info in context.findall(".//PoolInfo"):
            if info.get("Pool") == "TRI" and info.get("OddsType") == "0":
                
                return True
        return False
            
    def setStaticValues(self):
        pass
        
    def decode(self, context):
        matchNo = 1
        for info in context.findall(".//PoolInfo"):
            if info.get("Pool") == "TRI" and info.get("OddsType") == "0":
                i = 1
                for oddsInfo in info.findall(".//OddsInfo"):
                    self.data["combination_" + str(i) + "_combo"]["value"] = oddsInfo.get("Number")
                    
                    if oddsInfo.get("Odds").isnumeric():
                        self.data["combination_" + str(i) + "_odds"]["value"] = oddsInfo.get("Odds")
                        
                    #self.data["combination_" + str(i) + "_willpay"]["value"] = oddsInfo.get("WillPay")
                    self.data["match_id"]["value"] = util.ConstructMatchId(util.GetTodayDate(), matchNo, self.venue)
                    i = i + 1
                self.writeToDb()
                matchNo = matchNo + 1


if __name__ == "__main__":
    try: 
        tableName = "tri_odds_inplay_xml_odds"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = XmlScrapper(
            tableName, 
            XmlUrlGenerator(), 
            postgresClient,
            customWrite=True
        )

        scapper.Start()
    except Exception as error:
        logging.exception(error)