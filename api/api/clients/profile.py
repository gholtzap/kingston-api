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

def update_profile_picture(username: str, base64_image: str):
    accounts_collection, _ = get_collections()
    user = accounts_collection.find_one({"username": username})
    
    if not user:
        return {'error': 'User not found'}, 404
    
    # Compare the new base64 with the existing one
    if user.get('pfp') == base64_image:
        return {'error': 'You are uploading the same profile picture. Please choose a different image.'}, 409  # Conflict status code
    
    result = accounts_collection.update_one({'username': username}, {'$set': {'pfp': base64_image}})
    
    if result.modified_count == 0:
        return {'error': 'Failed to update profile picture.'}, 500
    
    return {'status': 'Profile picture updated successfully'}, 200



def fetch_user_data(username):
    accounts_collection, _ = get_collections()

    user_data = accounts_collection.find_one({"username": username}, {'password': 0})  # exclude password
    
    if not user_data:
        return {'error': 'User not found'}, 404

    user_data['pfp'] = f"data:image/jpeg;base64,{user_data['pfp']}" if user_data.get('pfp') else None

    return user_data