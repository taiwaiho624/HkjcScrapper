import logging
import datetime
import os 

def Init(appName="default"):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    dir = "logs/" + date + "/" + appName + "/"
    os.makedirs(dir, exist_ok=True)
    logging.basicConfig(
        filename= dir + datetime.datetime.now().strftime(appName + '_%Y_%m_%d-%H%M%S.log'),
        filemode='a',
        format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )

