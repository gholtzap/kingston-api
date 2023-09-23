from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash
from pymongo import MongoClient
from dotenv import load_dotenv
import os

print("Loading .env...")
load_dotenv()
mongodb_uri = os.getenv('MONGODB_URI')

def get_mongo_collection():
    client = MongoClient(mongodb_uri)
    db = client['theta']
    return db['accounts']

def login():
    try:
        collection = get_mongo_collection()

        data = request.json
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        user = collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            return jsonify({
                'message': 'Login successful!',
                'email': user['email'],
                'username': user.get('username', 'Unknown'),
                'role': user.get('role')
            }), 200        
        else:
            return jsonify({'error': 'Invalid email or password!'}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Server error'}), 500
