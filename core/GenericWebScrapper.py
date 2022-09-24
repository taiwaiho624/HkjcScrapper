from .GenericScrapper import GenericScrapper
from utils import request
from utils import htmlDecoder
import configparser


class GenericWebScrapper(GenericScrapper):
    def __init__(self, tableName, urlGenerator, postgresClient, isUpsert = False, duplicateChecker = None):
        super().__init__(tableName, urlGenerator, postgresClient, isUpsert = False, duplicateChecker = None)
        self.webData = {}
    
    def request(self, url):
        html = request.Request(url)
        decoder = htmlDecoder.HTMLDecoder(html)
        return decoder
    
    def init(self):
        super().init()
        
        config = configparser.ConfigParser()
        config.sections()
        config.read("config/" + self.tableName + ".ini")
        
        ####    Read XPath Info     ####
        data = dict(config.items(self.tableName + "XPath") )
        
        for key in data:
            self.webData[key] = {}
            self.webData[key]["xpath"] = data[key]
