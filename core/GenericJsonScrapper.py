from .GenericScrapper import GenericScrapper
from utils import request

class GenericJsonScrapper(GenericScrapper):
    def __init__(self, tableName, urlGenerator, postgresClient, isUpsert = False, duplicateChecker = None, customWrite = False, onlyRunOnRaceDay=True):
        super().__init__(tableName, urlGenerator, postgresClient, isUpsert, duplicateChecker, customWrite, onlyRunOnRaceDay)

    def request(self, url):
        try:
            res  = request.Request(url)
            return res.json() 
        except:
            return "{}"






