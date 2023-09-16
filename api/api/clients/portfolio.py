from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI
MONGODB_URI = os.getenv('MONGODB_URI')

def get_collections():
    # Setup MongoDB connection when needed
    client = MongoClient(MONGODB_URI)
    db = client['theta']  # Assuming the database name is 'theta'
    
    accounts_collection = db['accounts']
    portfolios_collection = db['clients-portfolio']
    
    return accounts_collection, portfolios_collection


def add_user_portfolio(username, portfolio):
    accounts_collection, portfolios_collection = get_collections()

    # Check if user exists
    user = accounts_collection.find_one({"username": username})
    if not user:
        return {'error': 'User not found'}, 404

    # Add/Update portfolio
    portfolios_collection.update_one(
        {"username": username},
        {"$set": {"portfolio": portfolio}},
        upsert=True  # If not exists, insert; otherwise, update
    )
    return {'status': 'Portfolio updated successfully'}, 200


def fetch_user_portfolio(username):
    _, portfolios_collection = get_collections()

    portfolio_data = portfolios_collection.find_one({"username": username})
    if not portfolio_data:
        return {'error': 'No portfolio found for this user'}, 404
    return portfolio_data['portfolio']


def initialize_portfolio(username, buys):
    accounts_collection, portfolios_collection = get_collections()
    
    # Ensure the user exists
    user = accounts_collection.find_one({"username": username})
    if not user:
        return {'error': 'User not found'}, 404

    # Insert portfolio for user
    portfolios_collection.update_one(
        {"username": username},
        {
            "$set": {
                "username": username,
                "holdings": buys
            }
        },
        upsert=True  # If user doesn't have a portfolio, create one
    )

    return {'status': 'Portfolio initialized successfully'}, 200


def add_stock_buy(username, ticker, shares, date):
    accounts_collection, portfolios_collection = get_collections()

    # Check if user exists
    user = accounts_collection.find_one({"username": username})
    if not user:
        return {'error': 'User not found'}, 404

    # Add the new stock buy to the holdings
    new_stock_buy = {
        "ticker": ticker,
        "shares": shares,
        "date": date
    }
    portfolios_collection.update_one(
        {"username": username},
        {"$push": {"holdings": new_stock_buy}},  # $push will add new_stock_buy to the holdings array
        upsert=True  # If user doesn't have a portfolio, create one
    )

    return {'status': 'Stock buy added successfully'}, 200
