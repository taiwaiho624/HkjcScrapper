from unittest import result
from core import GenericWebScrapper
from core import GenericUrlGenerator
from utils import postgresClient
from utils import logger
from utils import util
import logging
import datetime

class MatchinfoUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def Generate(self):
        race_day = util.GetTodayDate()

        for race_no in range(1,12):
            if self.isValid == False:
                self.isValid = True
                break
            
            dynamicFields = {
                        "match_id" : util.ConstructMatchDate(race_day, race_no),
                    }

            yield [f'https://bet.hkjc.com/racing/pages/odds_wp.aspx?lang=en&date={race_day}&raceno={race_no}', dynamicFields]
            


class MatchinfoScrapper(GenericWebScrapper.GenericWebScrapper):
    def isValid(self, context):
        expected_race_no = self.data["match_id"]["value"][-2:]
        website_race_no = context.GetText(self.webData["race_no"]['xpath'])

        website_race_no_str = str(util.GetNumberFromString(website_race_no)[0]).zfill(2)

        if website_race_no_str != expected_race_no:
            return False
        
        venue = context.GetText(self.webData["venue"]['xpath'])
        
        if venue == "Sha Tin":
            self.data["match_id"]["value"] = self.data["match_id"]["value"] + "ST"
        elif venue == "Happy Valley":
            self.data["match_id"]["value"] = self.data["match_id"]["value"] + "HV"
        return True 
     
    def decode(self, context):
        date = self.data["match_id"]["value"][:8]
        time = context.GetText(self.webData["start_time"]['xpath'])

        result = datetime.datetime.strptime(date + " " + time, "%Y%m%d %H:%M")
        self.data["start_time"]["value"] = result


if __name__ == "__main__":
    try: 
        tableName = "match_info"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = MatchinfoScrapper(
            tableName, 
            MatchinfoUrlGenerator(), 
            postgresClient,
            True
        )

        scapper.Start()
    except Exception as error:
        logging.exception(error)
