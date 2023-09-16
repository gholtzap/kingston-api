from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId
from flask.json import JSONEncoder


load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')

client = MongoClient(MONGODB_URI)
db = client['theta']

def get_portfolio_by_username(username):
    collection = db["clients-portfolio"]
    portfolio = collection.find_one({"username": username})
    return portfolio


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)
