from pymongo import MongoClient
import yfinance as yf
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv


load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')

def get_collections():
    client = MongoClient(MONGODB_URI)
    db = client['theta']
    
    accounts_collection = db['accounts']
    portfolios_collection = db['clients-portfolio']
    
    return accounts_collection, portfolios_collection

def fetch_stock_data(ticker, start_date, end_date=None):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    return data['Close']

def fetch_current_stock_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d") 

    if data.empty:
        print(f"No data available for {ticker}.")
        return 0
    return data['Close'].iloc[0]

def calculate_portfolio_value_for_user(username):
    accounts_collection, portfolios_collection = get_collections()
    user_portfolio = portfolios_collection.find_one({"username": username})

    # Debugging
    print(f"Fetched portfolio for user {username}:")
    print(user_portfolio)
    if not user_portfolio:
        return 0
    
    total_value = 0

    
    for holding in user_portfolio.get('holdings', []):
        try:
            ticker = holding['stock']
        except KeyError:
            print(f"KeyError: 'stock' key not found for holding: {holding}")
            continue
        ticker = holding['stock']
        shares = holding['quantity']

        # Get current price for the ticker
        current_price = fetch_current_stock_price(ticker)
        
        print(f"Current price for {ticker} is {current_price}. Number of shares is {shares}.")


        current_price = float(current_price)
        shares = int(shares)
        # Add the value of this holding to the total value
        total_value += current_price * shares

    print(f"Total calculated portfolio value for user {username} is {total_value}.")
    return total_value



def calculate_earnings_for_stock(ticker, shares, start_date):
    data = fetch_stock_data(ticker, start_date)
    
    purchase_price = data.iloc[0]
    current_price = data.iloc[-1]
    
    earnings = (current_price - purchase_price) * shares
    percent_return = (earnings / (purchase_price * shares)) * 100
    
    return earnings, percent_return

def calculate_earnings_for_interval(ticker, shares, start_date, end_date):
    data = fetch_stock_data(ticker, start_date, end_date)
    
    if data.empty:
        return 0, 0

    purchase_price = data.iloc[0]
    current_price = data.iloc[-1]
    
    earnings = (current_price - purchase_price) * shares
    percent_return = (earnings / (purchase_price * shares)) * 100
    
    return earnings, percent_return


def calculate_total_earnings(portfolio):
    total_earnings = 0
    total_percent_return = 0

    today = datetime.today().date()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)
    one_year_ago = today - timedelta(days=365)

    weekly_earnings = 0
    monthly_earnings = 0
    yearly_earnings = 0

    weekly_return = 0
    monthly_return = 0
    yearly_return = 0

    for holding in portfolio['holdings']:
        earnings, percent_return = calculate_earnings_for_stock(holding['ticker'], holding['shares'], holding['date'])
        total_earnings += earnings
        total_percent_return += percent_return 

        w_earnings, w_return = calculate_earnings_for_interval(holding['ticker'], holding['shares'], one_week_ago, today)
        weekly_earnings += w_earnings
        weekly_return += w_return

        m_earnings, m_return = calculate_earnings_for_interval(holding['ticker'], holding['shares'], one_month_ago, today)
        monthly_earnings += m_earnings
        monthly_return += m_return

        y_earnings, y_return = calculate_earnings_for_interval(holding['ticker'], holding['shares'], one_year_ago, today)
        yearly_earnings += y_earnings
        yearly_return += y_return

    # Average out the percent returns
    total_percent_return /= len(portfolio['holdings'])
    weekly_return /= len(portfolio['holdings'])
    monthly_return /= len(portfolio['holdings'])
    yearly_return /= len(portfolio['holdings'])

    return {
        'total_earnings': total_earnings,
        'total_percent_return': total_percent_return,
        'weekly_earnings': weekly_earnings,
        'weekly_return': weekly_return,
        'monthly_earnings': monthly_earnings,
        'monthly_return': monthly_return,
        'yearly_earnings': yearly_earnings,
        'yearly_return': yearly_return
    }
    
    
