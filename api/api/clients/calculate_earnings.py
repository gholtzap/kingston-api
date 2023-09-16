import yfinance as yf
from datetime import datetime, timedelta

def fetch_stock_data(ticker, start_date, end_date=None):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    return data['Close']

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
        total_percent_return += percent_return  # This will average out later

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