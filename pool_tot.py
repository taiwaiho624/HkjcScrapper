from unittest import result
from core import GenericJsonScrapper
from core import GenericUrlGenerator
from core import DuplicateChecker
from utils import postgresClient
from utils import logger
from utils import util
import logging

###############
#win 獨嬴
#place 位置
###############


#run once after race_day
class PoolTotUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def Generate(self):
        venues = ["S1", "S2", "HV", "ST"]
                
        race_day = util.GetTodayDate()
        for venue in venues:
            for race_no in util.RaceNoGenerator():
                if self.isValid == False:
                    self.isValid = True
                    break
                
                url = f'https://bet.hkjc.com/racing/getJSON.aspx?type=pooltot&date={race_day}&venue={venue}&raceno={race_no}'

                dynamicFields = {
                    "match_id" : util.ConstructMatchId(race_day, race_no, venue),
                }
                
                yield [url, dynamicFields]
            


class PoolTotScrapper(GenericJsonScrapper.GenericJsonScrapper):
    def isValid(self, context):
        if "inv" in context and "updateTime" in context and len(context["inv"]) > 0:
            return True 
        return False 

    def setStaticValues(self):
        self.data["status"]['value'] = 1 
        self.data["data_source"]['value'] = "hkjc"
        
    #can be abstracted
    def decode(self, context):
        outputs = context["inv"]
        for output in outputs:
            key = output["pool"].lower().replace('-',"")
            if key == "6up":
                key = "sixup"
            self.data[key]["value"] = output["value"]
        self.data["hkjc_updatetime"]["value"] = context["updateTime"]


if __name__ == "__main__":
    try: 
        tableName = "pool_tot"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = PoolTotScrapper(
            tableName, 
            PoolTotUrlGenerator(), 
            postgresClient,
            True
        )

        scapper.Start()
    except Exception as error:
        logging.exception(error)