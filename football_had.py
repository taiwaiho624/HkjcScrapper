from core import GenericJsonScrapper
from core import GenericUrlGenerator
from core import DuplicateChecker
from utils import postgresClient
from utils import logger
from utils import util
from utils import request
import logging
import time
import datetime
import sys

class FootballUrlGenerator(GenericUrlGenerator.GenericUrlGenerator):
    def __init__(self, date):
        super().__init__()
        self.fromDate = date 
    
    def Generate(self):
        for date in util.DateGeneratorNoSlash(self.fromDate):
            for page in range(1, 20):
                if self.isValid == False:
                    self.isValid = True
                    break
                url = f'https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate={date}&enddate={date}&teamid=default&pageno={page}'
                yield [url, {}]


class FootballScrapper(GenericJsonScrapper.GenericJsonScrapper):
    def isValid(self, context):
        if len(context) > 0: 
            return True

    def decode(self, context):
        for match in context[0]["matches"]:
            self.data["match_id"]["value"] = match["matchID"]
            self.data["match_id_official"]["value"] = match["matchIDinofficial"]
            self.data["home_team_name"]["value"] = match["homeTeam"]["teamNameCH"]
            self.data["away_team_name"]["value"] = match["awayTeam"]["teamNameCH"]
            self.data["had_result"]["value"] = match["hadodds"]["RES"]
            self.data["half_time_home_score"]["value"] = match["accumulatedscore"][0]["home"]
            self.data["half_time_away_score"]["value"] = match["accumulatedscore"][0]["away"]
            self.data["full_time_home_score"]["value"] = match["accumulatedscore"][1]["home"]
            self.data["full_time_away_score"]["value"] = match["accumulatedscore"][1]["away"]
            res = request.Request(f"https://bet.hkjc.com/football/getJSON.aspx?jsontype=last_odds.aspx&matchid={match['matchID']}").json()
            self.data["home_odds"]["value"] = res["hadodds"]["H"].split("@")[1]
            self.data["away_odds"]["value"] = res["hadodds"]["A"].split("@")[1]
            self.data["draw_odds"]["value"] = res["hadodds"]["D"].split("@")[1]
            self.writeToDb()


if __name__ == "__main__":
    try:
        tableName = "football_had"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        date = sys.argv[1]

        scapper = FootballScrapper(
            tableName, 
            FootballUrlGenerator(date), 
            postgresClient,
            onlyRunOnRaceDay=False,
            customWrite=True
        )

        scapper.Start()

    except Exception as error:
        logging.exception(error)
    