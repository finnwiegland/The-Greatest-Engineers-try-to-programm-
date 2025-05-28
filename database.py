from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_ADDRESS", "mongodb://root:example@mongodb:27017/")
client = MongoClient(MONGO_URI)

db = client["bim_sensor_db"]
