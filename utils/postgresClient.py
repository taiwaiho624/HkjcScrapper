

from configparser import ConfigParser
import logging
from optparse import Values
import psycopg2
from datetime import datetime

class PostGresClient:
    def __init__(self):
        self.conn = None
        self.tablename = None
        self.cursor = None
    
    def config(self, filename="env/database.ini", section="postgressql"):
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(filename)

        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        return db
    
    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            # read connection parameters
            params = self.config()

            # connect to the PostgreSQL server
            logging.info('Connecting to the PostgreSQL database...')
            self.conn = psycopg2.connect(**params)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)

    def Notify(self):
        now = datetime.now().strftime("%m/%d %H:%M:%S")
        self.cursor.execute(f"NOTIFY table_update, '{self.tablename},{now}';")

    def Execute(self, command):
        try:
            self.cursor.execute(command)
        except Exception as e:
            logging.error("Not able to execute command = " + command + " error=" + str(e))
            
    def CreateTableIfNotExist(self, tablename, data):
        self.tablename = tablename
        context = ""
        for key in data.keys():
            context += key + " " + data[key]["type"] + ","
            
        command = "CREATE TABLE IF NOT EXISTS {} ({});".format(tablename, context[:-1])
        
        self.Execute(command)            
        
    def InsertInto(self, tableName, data):
        values = ""
        keys   = "" 
        for key in data.keys():
            if data[key]["value"] == "N/A":
                continue
            
            if data[key]["type"] == "float8" or data[key]['type'] == "int":
                values += str(data[key]["value"])
            else:
                values += "'{}'".format(str(data[key]['value']))  
            keys   += key + ","
            values += ','
            
        command = "INSERT INTO {} ({}) VALUES ({})".format(tableName, keys[:-1], values[:-1])
        self.Execute(command)
        self.Notify()

    def Upsert(self, tableName, data, primary_key="match_id"):
        values = ""
        keys   = "" 
        update = ""
        for key in data.keys():
            if data[key]["value"] == "N/A":
                continue
            
            if data[key]["type"] == "float8" or data[key]['type'] == "int":
                values += str(data[key]["value"])
            else:
                values += "'{}'".format(str(data[key]['value']))  
            keys   += key + ","
            values += ','
            update += key + " = EXCLUDED." + key + ", "

    
        command = "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) DO UPDATE SET {}".format(tableName, keys[:-1], values[:-1], primary_key, update[:-2])
        self.Execute(command)
        self.Notify()
        
    
    def SelectInitSnapshot(self, tableName, group_key, keys, dayWithin = 5):
        keysCommnad = ",".join(keys)
        
        command = "SELECT {}, t.{}, timestamp FROM {} t INNER JOIN (SELECT {}, MAX(timestamp) as MaxTime FROM {} GROUP BY {})tm ON t.{} = tm.{} AND t.timestamp = tm.MaxTime".format(keysCommnad, group_key, tableName, group_key,tableName, group_key, group_key, group_key)
        self.Execute(command)
        rows = self.conn.cursor().fetchall()
        print(rows)
        return 
    
    def ReturnValue(self, cursor):
        colName = [desc[0] for desc in cursor.description]
        while 1:
            data = cursor.fetchone()
            if not data:
                break

            result = {}
            
            for i in range(len(data)):
                result[colName[i]] = data[i]

            yield result

    def SelectFromTable(self, tableName):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {tableName};")
        return self.ReturnValue(cursor) 
        
    def ExecuteCommand(self, command):
        cursor = self.conn.cursor()
        cursor.execute(command)
        return self.ReturnValue(cursor)        

        