import signal
import sys
import time

from pymongo import MongoClient

shutdown = False

def signal_handler(sig, frame):
    print('Gracefully shutting down')
    global shutdown
    shutdown = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

MONGO_CONNECTION_STR = 'mongodb://root:root@mongo:27017'

mongo_client = MongoClient(MONGO_CONNECTION_STR)
db = mongo_client['alertos']
collection = db['alerts']
alerts = list(collection.find())

while True:
    if shutdown:
        sys.exit()

    print(alerts)
    time.sleep(3)

# def load_stocks():

# if __name__ == '__main__':