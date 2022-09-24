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

if __name__ == "__main__":
    try:
        tableName = "qtt_odds_inplay"

        logger.Init(tableName)
                
        postgresClient = postgresClient.PostGresClient()
        postgresClient.connect()

        scapper = InplayOddsScrapper.InplayOddsScrapper(
            tableName, 
            InplayUrlGenerator.InplayUrlGenerator("qtttop"), 
            postgresClient
        )

        scapper.Start()

    except Exception as error:
        logging.exception(error)
    