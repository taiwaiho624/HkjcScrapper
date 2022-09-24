
class GenericUrlGenerator:
    def __init__(self):
        self.isValid = True 
    
    def NotifyIsValid(self, isValid):
        self.isValid = isValid
    
    #need to override for specific logic
    def Generate(self):
        pass 

