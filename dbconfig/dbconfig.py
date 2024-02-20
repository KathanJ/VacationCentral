from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

conn = MongoClient(MONGO_URI)
db = conn.Vacation_Central_DB