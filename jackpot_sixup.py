from unittest import result
from core import GenericWebScrapper
from core import GenericUrlGenerator
from utils import postgresClient
from utils import logger
from utils import util
import re
import logging

###############
#win 獨嬴
#place 位置
###############
venueMap = {
    "Happy Valley" : "HV",
    "Sha Tin" : "ST"
}

#run once after race_day
class JackpotUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def Generate(self):            
        race_day = util.GetTodayDate()

        url = f'https://bet.hkjc.com/racing/pages/odds_6up.aspx?lang=en&date={race_day}'

        dynamicFields = {
            "match_id" : race_day,
        }
        
        yield [url, dynamicFields]
            


class JackpotScrapper(GenericWebScrapper.GenericWebScrapper):
    def isValid(self, context):
        a = str(context.soup.find(lambda tag:tag.name=="td" and "Jackpot" in tag.text))
        a = a[a.find("Jackpot") :]
        a = a[a.find("$") + 1 : a.find("<")]
        a = a.replace(" ", "").replace("\r", "").replace("\n", "").replace(",","")
        if len(a) > 2:
            self.jackpot = a
            return True
        return False 

    def setStaticValues(self):
        pass
        
    def decode(self, context):
        venue = venueMap[context.GetText(self.webData["venue"]["xpath"])]
        a = str(context.soup.select('div[class*="raceNoOn_"]')[0])
        a = int(a[a.find("(") + 1:a.find(")")])
        self.data["sixup_jackpot"]["value"] = float(self.jackpot)
        self.data["match_id"]["value"] = util.ConstructMatchId(self.data["match_id"]["value"], a, venue)

if __name__ == "__main__":
    try: 
        tableName = "jackpot"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = JackpotScrapper(
            tableName, 
            JackpotUrlGenerator(), 
            postgresClient,
            True
        )

        scapper.Start()
    except Exception as error:
        logging.exception(error)