from core import GenericJsonScrapper
from core import GenericUrlGenerator
from utils import postgresClient
from utils import logger
from utils import util
import time

class InplayOddsScrapper(GenericJsonScrapper.GenericJsonScrapper):
    def isValid(self, context):
        if "OUT" in context and len(context["OUT"]) > 0:
            return True 
        return False 

    def setStaticValues(self):
        self.data["status"]['value'] = 1 
        self.data["data_source"]['value'] = "hkjc"
        
    #can be abstracted
    def decode(self, context):
        #print(context)
        outputs = context["OUT"].split(';')[1:]
        counter = 1
        for output in outputs:
            result = output.split('=')
            key = "combination_{}_combo".format(counter)
            self.data[key]["value"] = result[0]

            key = "combination_{}_odds".format(counter)
            self.data[key]["value"] = result[1]

            counter += 1