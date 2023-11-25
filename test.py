# import json
# from pymongo import MongoClient

# # Connect to MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# # client = MongoClient("mongodb://root:zuvaLabs@lab.zuvatech.com:27017/")


# # Select database and collection
# db = client["hhp-esm"]
# collection = db["roles"]

# # Read JSON file
# with open("roles.json") as f:
#     data = json.load(f)

# # Insert data into collection
# for i in data["roles"]:
#     print(i)
#     collection.update_one({"role": i["role"]}, {"$set": i}, upsert=True)

import datetime
