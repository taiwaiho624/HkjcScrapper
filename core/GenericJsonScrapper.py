from .GenericScrapper import GenericScrapper
from utils import request

class GenericJsonScrapper(GenericScrapper):
    def request(self, url):
        try:
            res  = request.Request(url)
            return res.json() 
        except:
            return "{}"






