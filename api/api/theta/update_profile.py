from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import os

load_dotenv()



MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in the environment variables.")



def get_accounts_collection():
    client = MongoClient(MONGODB_URI)
    db = client.theta
    return db.accounts

def update_user_profile(user_id, first_name, last_name, profile_picture):
    try:
        accounts_collection = get_accounts_collection()
        account_query = {"_id": ObjectId(user_id)}
        
        update_data = {}
        if first_name:
            update_data["firstName"] = first_name
        if last_name:
            update_data["lastName"] = last_name
        if profile_picture:
            update_data["profilePicture"] = profile_picture
        
        accounts_collection.update_one(account_query, {"$set": update_data})

        return {"message": "Profile updated successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def modify_role_in_db(target_username, new_role):
    try:
        collection = get_accounts_collection()

        # Update the role for the target username
        result = collection.update_one({'username': target_username}, {'$set': {'role': new_role}})

        # Check if the update was successful
        if result.modified_count == 1:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def modify_role(current_username, target_username, new_role):
    accounts_collection = get_accounts_collection()
    current_user = accounts_collection.find_one(current_username)

    if not current_user:
        return {'error': 'User not found'}, 404

    # Check if the current user has role 915
    if current_user['role'] != 915:
        return {'error': 'Permission denied'}, 403

    # Proceed to modify the role for the target user in your database
    result = modify_role_in_db(target_username, new_role)

    if result:
        return {'status': 'Role modified successfully'}, 200
    else:
        return {'error': 'Failed to modify role'}, 500