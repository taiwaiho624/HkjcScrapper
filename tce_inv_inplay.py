from core import GenericJsonScrapper
from core import GenericUrlGenerator
from core import DuplicateChecker
from utils import postgresClient
from utils import logger
from utils import util
import logging
import time
import datetime
from common import InplayUrlGenerator


class TceInvScrapper(GenericJsonScrapper.GenericJsonScrapper):
    def isValid(self, context):
        if "OUT" in context and len(context["OUT"]) > 20:
            return True 
        return False 

    def setStaticValues(self):
        self.data["status"]['value'] = 1 
        self.data["data_source"]['value'] = "hkjc"
        
    #can be abstracted
    def decode(self, context):
        #print(context)
        outputs = context["OUT"].split(';')[1:]
        for output in outputs:
            records = output.split('|')[1:]
            horse_no = output.split('|')[0]
            for record in records:
                rank = record.split('=')[0]
                inv  = record.split('=')[1]
                self.data[f"horse_{horse_no}_rank_{rank}_inv"]["value"] = inv

            
if __name__ == "__main__":
    try:
        tableName = "tce_inv_inplay"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = TceInvScrapper(
            tableName, 
            InplayUrlGenerator.InplayUrlGenerator("tceinv", "oneTime"), 
            postgresClient
        )

        scapper.Start()

    except Exception as error:
        logging.exception(error)
    