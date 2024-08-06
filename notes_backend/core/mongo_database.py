import os
from pymongo import MongoClient


class MONGODB:
    def __init__(self):
        self.APP_MODE = os.getenv('APP_MODE', default='DEV')
        self.HOST = os.getenv('MONGO_HOST')
        self.PORT = os.getenv('MONGO_PORT')
        self.USERNAME = os.getenv('MONGO_USER')
        self.PASSWORD = os.getenv('MONGO_PASS')
        self.DB = os.getenv('MONGO_DB')

        self.MONGO_URL = 'mongodb://{}:{}@{}:{}?retryWrites=true&w=majority&authSource=admin'.format(self.USERNAME,
                                                                                                     self.PASSWORD,
                                                                                                     self.HOST,
                                                                                                     self.PORT,
                                                                                                     self.DB)

        if self.APP_MODE == "BETA" or self.APP_MODE == 'PROD':
            self.MONGO_URL = 'mongodb+srv://{}:{}@{}?retryWrites=true&w=majority&authSource=admin'.format(self.USERNAME,
                                                                                                          self.PASSWORD,
                                                                                                          self.HOST,
                                                                                                          self.DB)

        self.mongodb_client = MongoClient(self.MONGO_URL)
        self.db = self.mongodb_client[self.DB]

    def get_db(self):
        return self.db

    def shutdown_db(self):
        self.mongodb_client.close()

    def drop_database(self):
        self.mongodb_client.drop_database(self.DB)

    def check_connection(self):
        try:
            if self.mongodb_client.get_database(self.DB):
                return True
        except:
            return False

    def reconnect(self):
        self.mongodb_client = MongoClient(self.MONGO_URL)
        self.db = self.mongodb_client[self.DB]


MONGO = MONGODB()
MONGO_CLIENT = MONGO.mongodb_client
DB = MONGO.db
