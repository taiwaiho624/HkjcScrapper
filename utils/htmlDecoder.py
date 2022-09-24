from lxml import etree
from bs4 import BeautifulSoup

class HTMLDecoder:
    def __init__(self, html):
        self.soup = BeautifulSoup( html.content , 'html.parser')
        self.etree = etree.HTML(html.content)

    def GetText(self, xpath):
        result = self.etree.xpath(xpath + "/text()")
        if len(result) == 0:
            return None 
        else :
            return self.etree.xpath(xpath + "/text()")[0]
    
    def GetAlt(self, xpath):
        result = self.etree.xpath(xpath + "/@alt")
        if len(result) == 0:
            return None 
        else :
            return self.etree.xpath(xpath + "/@alt")

    def GetDouble(self, xpath):
        return float(self.etree.xpath(xpath + "/text()")[0])


    def Get(self, xpath):
        return self.etree.xpath(xpath)