from .GenericScrapper import GenericScrapper
from utils import request
import xml.etree.ElementTree as ET

class GenericXmlScrapper(GenericScrapper):
    def request(self, url):
        try:
            res  = request.Request(url)
            return ET.ElementTree(ET.fromstring(res.text)).getroot() 
        except:
            return "{}"