from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re

# Loading environment variables only once
print("Loading .env...")
load_dotenv()
mongodb_uri = os.getenv('MONGODB_URI')

# Removed unnecessary Flask app instantiation as you're not defining routes in this module

def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def get_mongo_collection():
    # This function ensures that MongoDB connection is established only when needed.
    client = MongoClient(mongodb_uri)
    db = client['theta']
    return db['accounts']

def register():
    try:
        collection = get_mongo_collection()

        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing data'}), 400
        if len(username) < 3 or len(password) < 8:
            return jsonify({'error': 'Username or password too short'}), 400
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        user_exists = collection.find_one({'email': email})
        if user_exists:
            return jsonify({'error': 'User already exists!'}), 400

        hashed_password = generate_password_hash(password)

        new_user = {
            "username": username,
            "email": email,
            "password": hashed_password
        }

        collection.insert_one(new_user)

        return jsonify({'message': 'User created successfully!'}), 201

    except Exception as e:
        print(f"Error: {e}") 
        return jsonify({'error': 'Server error'}), 500 
