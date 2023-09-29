import matplotlib
import matplotlib.dates as mdates
import seaborn as sns
import os
import yfinance as yf
import pandas as pd
import json
from .clients.profile import update_profile_picture, fetch_user_data
from .clients.calculate_earnings import calculate_total_earnings, calculate_portfolio_value_for_user, fetch_current_stock_price
from .clients.portfolio_display import get_portfolio_by_username
from .clients.portfolio import delete_buys_from_portfolio, edit_buy_in_portfolio, delete_buy_from_portfolio, add_stock_to_portfolio, initialize_portfolio
from .beta.beta import generate_index_and_image
from .beta.save_index import fetch_saved_indexes
from .beta.save_index import save_user_index as core_save_index
from .theta.register import register
from .theta.update_profile import update_user_profile, modify_role
from .theta.login import login
from .alpha.alpha import calculate_decisions
from http.client import BAD_REQUEST
from flask import Blueprint, request, send_file, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from pymongo import MongoClient


print("Starting alpha imports ...")

print("Starting theta imports ...")

print("Starting beta imports ...")

print("Starting clients imports ...")

print("Starting profile imports ... ")
print("Finished local module imports...")


matplotlib.use('Agg')


# Blueprints

auth_bp = Blueprint('auth_bp', __name__)
tickers_bp = Blueprint('tickers_bp', __name__)
profile_bp = Blueprint('profile_bp', __name__)


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


@auth_bp.route('/login', methods=['POST'])
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
        result = update_user_profile(
            user_id, first_name, last_name, profile_picture)
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
####################### CLIENT PROFILE  ########################
################################################################


@profile_bp.route('/update_pfp', methods=['POST'])
def update_profile_picture_route():
    try:
        print("Entering update_pfp route")  # Debug Print
        data = request.get_json()
        print(f"Received data: {data}")  # Debug Print

        username = data.get('username')
        base64_image = data.get('image')

        if not username or not base64_image:
            return jsonify({'error': 'Username and image are required'}), 400

        print("Calling update_profile_picture function")  # Debug Print
        result, status_code = update_profile_picture(username, base64_image)
        print(f"Result from update_profile_picture: {result}")  # Debug Print

        return jsonify(result), status_code
    except Exception as e:
        # Ensure this gets printed
        print(f"Unexpected error in update_profile_picture_route: {e}")
        return jsonify({"error": "Internal server error"}), 500


@profile_bp.route('/user/<string:username>', methods=['GET'])
def get_user_data(username):
    user_data = fetch_user_data(username)

    if 'error' in user_data:
        return jsonify(user_data), 404
    else:
        return jsonify(user_data)
    
################################################################
###################### CLIENT PORTFOLIO ########################
################################################################


portfolio_bp = Blueprint('portfolio_bp', __name__)


@portfolio_bp.route('/portfolio_value/<username>', methods=['GET'])
def get_portfolio_value(username):
    value = calculate_portfolio_value_for_user(username)
    return jsonify({'portfolio_value': value})


@portfolio_bp.route('/market-data', methods=['GET'])
def get_market_data():
    sp500_price = fetch_current_stock_price("^GSPC")
    dow_jones_price = fetch_current_stock_price("^DJI")

    return jsonify({
        'sp500': sp500_price,
        'dow_jones': dow_jones_price
    })

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
    print(data)
    username = data.get('username')
    ticker = data.get('ticker')
    quantity = data.get('quantity')
    price = data.get('price')

    if not all([username, ticker, quantity, price]):
        return jsonify({"error": "Missing required parameters"}), 400

    result, status_code = add_stock_to_portfolio(
        username, ticker, quantity, price)
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
    ticker = data.get('stock') 
    shares = data.get('quantity') 
    price = data.get('price')

    if not username or not buy_id:
        return jsonify({'error': 'Username or buy ID missing'}), 400

    response, status = edit_buy_in_portfolio(username, buy_id, ticker, shares, price)
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

@portfolio_bp.route('/portfolio/delete-buys', methods=['POST'])
def delete_buys():
    data = request.get_json()
    username = data.get('username')
    buy_ids = data.get('buy_ids')

    if not username or not buy_ids:
        return jsonify({'error': 'Username or buy IDs missing'}), 400

    response, status = delete_buys_from_portfolio(username, buy_ids)
    return jsonify(response), status