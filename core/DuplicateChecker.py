
class DuplicateChecker:
    def __init__(self, tableName, primary_key, keys, postgresClient):
        self.primary_key = primary_key
        self.tableName = tableName 
        self.keys = keys
        self.lastWriteSnapShot = {}
        self.postgresClient = postgresClient
        
    def InitLastWriteSnapShot(self):
        self.postgresClient.SelectInitSnapshot(self.tableName, self.primary_key, self.keys)
        
    
    def SaveLastWriteSnapShot(self, data):
        primary_key_value = data[self.primary_key]["value"]
        
        if primary_key_value not in self.lastWriteSnapShot:
            self.lastWriteSnapShot[primary_key_value] = {}
        
        for key in self.keys:
            self.lastWriteSnapShot[primary_key_value][key] = data[key]["value"]
    
    def IsDuplicate(self, data):
        primary_key_value = data[self.primary_key]["value"]
        if primary_key_value not in self.lastWriteSnapShot:
            return False 

        for key in self.keys:
            if data[key]["value"] != self.lastWriteSnapShot[primary_key_value][key]:
                return False 
        
        return True 
        