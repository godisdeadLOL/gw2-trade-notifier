import pymongo
from config import config

client = pymongo.AsyncMongoClient(config.mongo_url)
db = client.get_database(config.app_name)
