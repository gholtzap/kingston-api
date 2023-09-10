from api import app

print("Starting Flask app from run.py...")  # New print statement

if __name__ == "__main__":
    print("Inside main block in run.py...")  # New print statement
    app.run(debug=True)
