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
    
    # Assign IDs to the buys
    for i, buy in enumerate(buys, 1):  # Starting index from 1
        buy['id'] = i

    # Insert the portfolio for the user
    portfolios_collection.update_one(
        {"username": username},
        {
            "$set": {
                "username": username,
                "last_buy_id": len(buys),  # set last_buy_id to the total number of buys added initially
                "holdings": buys
            }
        },
        upsert=True  # If the user doesn't have a portfolio, create one
    )

    return {'status': 'Portfolio initialized successfully'}, 200


def add_stock_buy(username, ticker, shares, date):
    accounts_collection, portfolios_collection = get_collections()

    # Check if user exists
    user = accounts_collection.find_one({"username": username})
    if not user:
        return {'error': 'User not found'}, 404

    # Fetch the user's current portfolio
    user_portfolio = portfolios_collection.find_one({"username": username})
    
    # Determine the new buy's ID
    if user_portfolio and 'last_buy_id' in user_portfolio:
        new_id = user_portfolio['last_buy_id'] + 1
    else:
        new_id = 1

    # Create the new buy
    new_stock_buy = {
        "id": new_id,
        "ticker": ticker,
        "shares": shares,
        "date": date
    }

    # Update the user's portfolio
    portfolios_collection.update_one(
        {"username": username},
        {
            "$push": {"holdings": new_stock_buy},
            "$set": {"last_buy_id": new_id}
        },
        upsert=True  # If user doesn't have a portfolio, create one
    )

    return {'status': 'Stock buy added successfully'}, 200


def add_stock_to_portfolio(username: str, ticker: str, quantity: int, date: str) -> dict:
    _, portfolios_collection = get_collections()
    # Check if user exists
    user_portfolio = portfolios_collection.find_one({"username": username})
    if not user_portfolio:
        return {"error": "User not found"}, 404

    # Add the new stock to the holdings
    new_holding = {
        "ticker": ticker,
        "shares": quantity,
        "date": date
    }
    portfolios_collection.update_one(
        {"username": username},
        {"$push": {"holdings": new_holding}}
    )

    return {"status": "Stock added successfully"}, 200


def delete_buy_from_portfolio(username, buy_id):
    _, portfolios_collection = get_collections()
    
    # Ensure the user exists
    user_portfolio = portfolios_collection.find_one({"username": username})
    if not user_portfolio:
        return {'error': 'Portfolio not found for this user'}, 404

    # Remove buy with the given ID from the holdings
    result = portfolios_collection.update_one(
        {"username": username},
        {"$pull": {"holdings": {"id": buy_id}}}  # $pull will remove the matching subdocument from the holdings array
    )

    # Check if the operation was successful
    if result.modified_count == 0:
        return {'error': 'No buy found with the provided ID or other error occurred'}, 404

    return {'status': 'Buy removed successfully'}, 200

def edit_buy_in_portfolio(username, buy_id, ticker=None, shares=None, date=None):
    _, portfolios_collection = get_collections()

    # Ensure the user exists
    user_portfolio = portfolios_collection.find_one({"username": username})
    if not user_portfolio:
        return {'error': 'Portfolio not found for this user'}, 404

    # Build the update query based on provided fields
    update_fields = {}
    if ticker:
        update_fields["holdings.$.ticker"] = ticker
    if shares is not None:  # Checking for None because shares can be 0
        update_fields["holdings.$.shares"] = shares
    if date:
        update_fields["holdings.$.date"] = date

    # Update the buy with given ID in the holdings
    result = portfolios_collection.update_one(
        {"username": username, "holdings.id": buy_id},
        {"$set": update_fields}
    )

    # Check if the operation was successful
    if result.modified_count == 0:
        return {'error': 'No buy found with the provided ID or other error occurred'}, 404

    return {'status': 'Buy updated successfully'}, 200