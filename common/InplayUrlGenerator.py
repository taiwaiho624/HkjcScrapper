from core import GenericJsonScrapper
from core import GenericUrlGenerator
from utils import postgresClient
from utils import logger
from utils import util
import time

class InplayUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def __init__(self, type, mode="nonStop", timeout=5):
        self.type = type
        self.timeout = timeout 
        self.mode = mode
        super().__init__()

    def OneTime(self):
        venues = ["S1", "S2", "HV", "ST"]
                
        race_day = util.GetTodayDate()

        for venue in venues:
            for race_no in util.RaceNoGenerator():
                if self.isValid == False:
                    self.isValid = True
                    break
                                    
                url = f'https://bet.hkjc.com/racing/getJSON.aspx?type={self.type}&date={race_day}&venue={venue}&raceno={race_no}'

                dynamicFields = {
                    "match_id" : util.ConstructMatchId(race_day, race_no, venue)
                }

                yield [url, dynamicFields]

    def NonStop(self):
        venues = ["S1", "S2", "HV", "ST"]
                
        race_day = util.GetTodayDate()

        while True:
            for venue in venues:
                for race_no in util.RaceNoGenerator():
                    if self.isValid == False:
                        self.isValid = True
                        break
                                        
                    url = f'https://bet.hkjc.com/racing/getJSON.aspx?type={self.type}&date={race_day}&venue={venue}&raceno={race_no}'

                    dynamicFields = {
                        "match_id" : util.ConstructMatchId(race_day, race_no, venue)
                    }
                    
                    yield [url, dynamicFields]
            
            time.sleep(self.timeout)
    
    def Generate(self):
        if self.mode == "nonStop":
            return self.NonStop()
        else:
            return self.OneTime()