from flask import Blueprint, request, send_file, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from pymongo import MongoClient


print("Starting alpha imports ...")
from .alpha.alpha import calculate_decisions

print("Starting theta imports ...")
from .theta.login import login
from .theta.update_profile import update_user_profile, modify_role
from .theta.register import register

print("Starting beta imports ...")
from .beta.save_index import save_user_index as core_save_index
from .beta.save_index import fetch_saved_indexes
from .beta.beta import generate_index_and_image

print("Starting clients imports ...")
from .clients.portfolio import edit_buy_in_portfolio, delete_buy_from_portfolio, add_stock_to_portfolio, initialize_portfolio
from .clients.portfolio_display import get_portfolio_by_username
from .clients.calculate_earnings import calculate_total_earnings

print("Finished local module imports...")

import json
import pandas as pd

import yfinance as yf

import os
import seaborn as sns

import matplotlib.dates as mdates
import matplotlib
matplotlib.use('Agg')


# Blueprints 

auth_bp = Blueprint('auth_bp', __name__)
tickers_bp = Blueprint('tickers_bp', __name__)


################################################################ 
######################### TICKERS BP ###########################
################################################################ 


@tickers_bp.route('/alpha', methods=['POST'])
def tickers():
    data = request.json
    tickers = data.get('tickers')
    if not tickers:
        return {'error': 'No tickers provided'}, 400

    try:
        result = calculate_decisions(tickers)
        return {'result': result}
    except Exception as e:
        return {'error': str(e)}, 500

@tickers_bp.route('/beta', methods=['POST'])
def beta():
    data = request.json
    if not data:
        return {'error': 'No data provided'}, 400

    try:
        result = generate_index_and_image(data)
        return result, 200, {'ContentType': 'application/json'}
    except Exception as e:
        return {'error': str(e)}, 500
    
@tickers_bp.route('/saveIndex', methods=["POST"])
def save_index():
    data = request.json
    if not data:
        return {'error': 'No data provided'}, 400

    try:
        result = core_save_index(data)
        return result
 
    except Exception as e:
        return {'error': str(e)}, 500


@tickers_bp.route('/getSavedIndexes', methods=["GET"])
def get_saved_indexes_endpoint():
    username = request.args.get("username")
    if not username:
        return {'error': 'Username not provided'}, 400

    try:
        result = fetch_saved_indexes(username)
        return result
    except Exception as e:
        return {'error': str(e)}, 500


################################################################ 
####################### AUTHENTICATION #########################
################################################################ 

@auth_bp.route('/signup', methods=['POST'])
def backend_signup():
    return register()

@auth_bp.route('/login', methods = ['POST'])
def backend_login():
    return login()

@auth_bp.route('/updateProfile', methods=['POST'])
def update_profile():
    user_id = request.form.get("userId")
    first_name = request.form.get("firstName")
    last_name = request.form.get("lastName")

    profile_picture = None
    if 'profilePicture' in request.files:
        file = request.files['profilePicture']
        if file.filename != '':
            filename = secure_filename(file.filename)
            profile_picture = file.read()

    try:
        result = update_user_profile(user_id, first_name, last_name, profile_picture)
        return result
    except Exception as e:
        return {'error': str(e)}, 500

@auth_bp.route('/modify-role', methods=['POST'])
def modify_user_role():
    # Extract the data from the frontend request
    data = request.json
    current_username = data.get('current_username')
    target_username = data.get('target_username')
    new_role = data.get('new_role')

    # Use the logic function to handle the modification
    result, status = modify_role(current_username, target_username, new_role)

    return jsonify(result), status


################################################################ 
###################### CLIENT PORTFOLIO ########################
################################################################ 

portfolio_bp = Blueprint('portfolio_bp', __name__)



# Create
@portfolio_bp.route('/portfolio/initialize', methods=['POST'])
def initialize_portfolio_route():
    data = request.get_json()
    username = data.get('username')
    buys = data.get('buys')

    if not username or not buys:
        return jsonify({'error': 'Username and buys are required'}), 400
    
    result, status_code = initialize_portfolio(username, buys)
    return jsonify(result), status_code

@portfolio_bp.route('/portfolio/add', methods=['POST'])
def add_portfolio():
    data = request.json
    username = data.get('username')
    ticker = data.get('ticker')
    quantity = data.get('quantity')
    date = data.get('date')
    
    if not all([username, ticker, quantity, date]):
        return jsonify({"error": "Missing required parameters"}), 400

    result, status_code = add_stock_to_portfolio(username, ticker, quantity, date)
    return jsonify(result), status_code

# Read
@portfolio_bp.route('/portfolio/<string:username>', methods=['GET'])
def get_portfolio(username):
    portfolio = get_portfolio_by_username(username)
    
    if portfolio:
        return jsonify(portfolio)
    else:
        return jsonify({"error": "Portfolio not found for the given username"}), 404

@portfolio_bp.route('/earnings/<string:username>', methods=['GET'])
def get_earnings(username):
    portfolio = get_portfolio_by_username(username)
    
    if not portfolio:
        return jsonify({"error": "Portfolio not found for the given username"}), 404

    earnings_data = calculate_total_earnings(portfolio)
    
    return jsonify(earnings_data)

# Update
@portfolio_bp.route('/portfolio/edit-buy', methods=['POST'])
def edit_buy():
    data = request.get_json()
    username = data.get('username')
    buy_id = data.get('buy_id')
    ticker = data.get('ticker')
    shares = data.get('shares')
    date = data.get('date')

    if not username or not buy_id:
        return jsonify({'error': 'Username or buy ID missing'}), 400

    response, status = edit_buy_in_portfolio(username, buy_id, ticker, shares, date)
    return jsonify(response), status


# Delete
@portfolio_bp.route('/portfolio/delete-buy', methods=['POST'])
def delete_buy():
    data = request.get_json()
    username = data.get('username')
    buy_id = data.get('buy_id')

    if not username or not buy_id:
        return jsonify({'error': 'Username or buy ID missing'}), 400

    response, status = delete_buy_from_portfolio(username, buy_id)
    return jsonify(response), status



    
    