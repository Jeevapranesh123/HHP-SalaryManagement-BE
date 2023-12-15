import pymongo

client = pymongo.MongoClient("localhost", 27017)

db = client["hhp-esm"]

collections = db.list_collection_names()

required_collections = ["roles", "employees", "users"]

collections = list(set(collections) - set(required_collections))

for collection in collections:
    db[collection].drop()
