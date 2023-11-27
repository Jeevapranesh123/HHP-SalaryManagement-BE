import json
from pymongo import MongoClient
import sys

# Connect to MongoDB
local_client = MongoClient("mongodb://localhost:27017/")
cloud_client = MongoClient("mongodb://root:zuvaLabs@lab.zuvatech.com:27017/")

# Check if the queue name is passed as an argument
if len(sys.argv) < 2:
    print("Usage: python script_name.py [local|cloud]")
    sys.exit(1)

type = sys.argv[1]

if type == "local":
    client = local_client

elif type == "cloud":
    client = cloud_client

else:
    print("Usage: python script_name.py [local|cloud]")
    sys.exit(1)

# Select database and collection
db = client["hhp-esm"]
collection = db["roles"]

# Read JSON file
with open("roles.json") as f:
    data = json.load(f)

# Insert data into collection
for i in data["roles"]:
    print(i)
    collection.update_one({"role": i["role"]}, {"$set": i}, upsert=True)
