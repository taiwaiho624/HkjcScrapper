from core import GenericJsonScrapper
from core import GenericUrlGenerator
from core import DuplicateChecker
from utils import postgresClient
from utils import logger
from utils import util
import logging
import time
import datetime

class WinOddsUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def Generate(self):
        venues = ["S1", "S2", "HV", "ST"]
                
        race_day = util.GetTodayDate()

        while True:
            for venue in venues:
                for race_no in util.RaceNoGenerator():
                    if self.isValid == False:
                        self.isValid = True
                        break
                                        
                    url = f'https://bet.hkjc.com/racing/getJSON.aspx?type=win&date={race_day}&venue={venue}&raceno={race_no}'

                    dynamicFields = {
                        "match_id" : util.ConstructMatchId(race_day, race_no, venue),
                    }
                    
                    yield [url, dynamicFields]
            time.sleep(5)



class WinOddsScrapper(GenericJsonScrapper.GenericJsonScrapper):
    def isValid(self, context):
        if "OUT" in context and len(context["OUT"]) > 0:
            return True 
        return False 

    def setStaticValues(self):
        self.data["status"]['value'] = 1 
        self.data["data_source"]['value'] = "hkjc"
        
    #can be abstracted
    def decode(self, context):
        outputs = context["OUT"].split(';')[1:]
        for output in outputs:
            result = output.split('=')
            key = "horse_{}_odds".format(result[0])
            value = result[1]
            if value == "SCR":
                value = "-1"
            self.data[key]["value"] = value
            
if __name__ == "__main__":
    try:
        tableName = "win_odds_inplay"

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
    