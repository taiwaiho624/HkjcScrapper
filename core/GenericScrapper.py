from numpy import False_
from utils import postgresClient
from utils import request
from utils import util
import configparser
import logging

class GenericScrapper:
    def __init__(self, tableName, urlGenerator, postgresClient, isUpsert = False, duplicateChecker = None, customWrite = False):
        self.tableName = tableName
        self.data = {}
        self.urlGenerator = urlGenerator
        self.postgresClient = postgresClient
        
        self.customWrite = customWrite
        self.isUpsert = isUpsert
        self.duplicateChecker = duplicateChecker

    def init(self):
        config = configparser.ConfigParser()
        config.sections()
        config.read("config/" + self.tableName + ".ini")

        ####    Read Table Info     ####
        data = dict(config.items(self.tableName + "Table") )
        
        for key in data:
            self.data[key]= {}
            self.data[key]["type"] = data[key]
            self.data[key]["value"] = "N/A"
        
        ####    Create Table if not exist   ####
        self.postgresClient.CreateTableIfNotExist(self.tableName, self.data)
    
    def initLastWriteSnapShot(self):
        if self.duplicateChecker == None:
            return
         
        self.duplicateChecker.InitLastWriteSnapShot()
    
    def saveLastWriteSnapShot(self):
        if self.duplicateChecker == None:
            return 

        self.duplicateChecker.SaveLastWriteSnapShot(self.data)

    def isDuplicate(self):
        if self.duplicateChecker == None:
            return False 
        
        self.duplicateChecker.IsDuplicate(self.data)
    
    def setStaticValues(self):
        pass
    
    def writeToDb(self):
        if self.isUpsert:
            self.postgresClient.Upsert(self.tableName, self.data)
        else:
            self.postgresClient.InsertInto(self.tableName, self.data)

    def request(self, url):
        pass 

    def isValid(self, context):
        return False 
    
    def decode(self, context):
        pass
    
    def setDynamicValues(self, dynamicValues):
        for key in dynamicValues.keys():
            self.data[key]["value"] = dynamicValues[key]
    
    def cleanValue(self):
        for key in self.data.keys():
            self.data[key]["value"] = "N/A"
    
    def setRequestTime(self):
        if "request_time" in self.data:
            self.data["request_time"]["value"] = util.GetCurrentTimeStamp()

    def setResponseTime(self):
        if "response_time" in self.data:
            self.data["response_time"]["value"] = util.GetCurrentTimeStamp()

    def Start(self):
        self.init()
        #self.initLastWriteSnapShot()
        for url, dynamicFields in self.urlGenerator.Generate():
            try:
                self.cleanValue()
                self.setDynamicValues(dynamicFields)
                self.setStaticValues()
                
                self.setRequestTime()
                context = self.request(url)
                
                if not self.isValid(context):
                    self.urlGenerator.NotifyIsValid(False)
                    logging.info("It is not an valid url=" + url)
                    continue 
                logging.info("Processing url=" + url)

                self.urlGenerator.NotifyIsValid(True)
                
                self.setResponseTime()
                self.decode(context)
                
                if self.isDuplicate():
                    logging.info("It is deplicated data, so we dont write to db url=" + url)
                    continue
                
                if self.customWrite == False:
                    self.writeToDb()
                self.saveLastWriteSnapShot()

            except Exception as error:
                logging.exception(error)
                continue
    
