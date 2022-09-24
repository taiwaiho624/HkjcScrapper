from core import GenericJsonScrapper
from core import GenericUrlGenerator
from core import DuplicateChecker
from utils import postgresClient
from utils import logger
from utils import util
import logging
import time
import datetime
from common import InplayOddsScrapper
from common import InplayUrlGenerator

class JkcOddsUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def Generate(self):
        venues = ["S1", "S2", "HV", "ST"]
                
        race_day = util.GetTodayDate()

        while True:
            for venue in venues:                                    
                url = f'https://bet.hkjc.com/racing/getJSON.aspx?type=jkc&date={race_day}&venue={venue}'

                dynamicFields = {
                    "match_id" : util.ConstructMatchId(race_day, 1, venue)
                }
                
                yield [url, dynamicFields]

            time.sleep(60)

class JkcOddsScrapper(GenericJsonScrapper.GenericJsonScrapper):
    def isValid(self, context):
        if "S" in context and len(context["S"]) > 0:
            return True 
        return False 

    def setStaticValues(self):
        self.data["status"]['value'] = 1 
        self.data["data_source"]['value'] = "hkjc"
        
    #can be abstracted
    def decode(self, context):
        counter = 1
        for racer in context['S']:
            self.data["jkc_" + str(counter) + "_code"]['value'] = racer['code']
            self.data["jkc_" + str(counter) + "_op_odds"]['value'] = racer['opOdds']
            self.data["jkc_" + str(counter) + "_latest_odds"]['value'] = racer['latestOdds']

            counter += 1

if __name__ == "__main__":
    try:
        tableName = "jkc_odds_inplay"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = JkcOddsScrapper(
            tableName, 
            JkcOddsUrlGenerator(), 
            postgresClient
        )

        scapper.Start()

    except Exception as error:
        logging.exception(error)
    