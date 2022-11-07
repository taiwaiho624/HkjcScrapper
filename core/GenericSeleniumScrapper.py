from .GenericScrapper import GenericScrapper
from utils import selenium_request
from utils import htmlDecoder
import configparser

class GenericSeleniumScrapper(GenericScrapper):
    def request(self, url):
        soup = selenium_request.Request(url)
        return soup