from utils import request
from utils import util
import requests

url1 = "https://iosbsinfo01.hkjc.com/infoA/AOSBS/HR_GetInfo.ashx?QT=HR_ODDS_ALL&Race=*&Venue=*&Result=1&Dividend=1&JTC=1&JKC=1&TNC=1&Lang=zh-HK"
url2 = "https://iosbsinfo02.hkjc.com/infoA/AOSBS/HR_GetInfo.ashx?QT=HR_ODDS_ALL&Race=*&Venue=*&Result=1&Dividend=1&JTC=1&JKC=1&TNC=1&Lang=zh-HK"

currentTimeStamp = util.GetCurrentTimeStamp()

res = requests.get(url1)

with open("data/" + currentTimeStamp + '-01.xml', 'w') as f:
    f.write(res.text)

res = requests.get(url2)

with open("data/" + currentTimeStamp + '-02.xml', 'w') as f:
    f.write(res.text)
