from utils import request
from utils import util
import requests
import time


url = "https://iosbsinfo02.hkjc.com/infoA/AOSBS/HR_GetInfo.ashx?QT=HR_ODDS_ALL&Race=*&Venue=*&Result=1&Dividend=1&JTC=1&JKC=1&TNC=1&Lang=zh-HK"

while True:
    currentTimeStamp = util.GetCurrentTimeStamp()

    res = requests.get(url)

    with open("data/" + currentTimeStamp + '.xml', 'w') as f:
        f.write(res.text)

    time.sleep(5)