# Importing the necessary Libraries
import requests as r
from bs4 import BeautifulSoup
from dataclasses import dataclass
import time
import sqlite3
from tabulate import tabulate  

# Stock --> Position --> Portfolio


def my_db(ticker, exchange, quantity):
    # Connect to the SQLite database file "my_stocks_db.db" or create it if it doesn't exist
    conn = sqlite3.connect("my_stocks_db.db")
    
    # Create a cursor object to execute SQL queries on the database
    cursor = conn.cursor()
    
     # Define the SQL query to create the "stock_table" if it doesn't already exist
    create_table_query = """
        CREATE TABLE IF NOT EXISTS stock_table (
            Ticker TEXT PRIMARY KEY,
            Exchange TEXT,
            Quantity INTEGER
        )
    """
     # Execute the query to create the "stock_table" if it doesn't already exist
    cursor.execute(create_table_query)
    
    # Define the SQL query to select a row from the "stock_table" with the provided "ticker"
    select_query = "SELECT Ticker FROM stock_table WHERE Ticker = ?"
    
    # Execute the select query with the "ticker" as a parameter to check if the ticker already exists in the table
    cursor.execute(select_query, (ticker,))
    
    # Fetch the first result (if any) from the query, which will be the existing "ticker" if it's found in the table
    existing_ticker = cursor.fetchone()
    
    # Checking if the "ticker" already exists in the "stock_table"
    if existing_ticker:
        # If the "ticker" exists, define the SQL query to update the "Exchange" and "Quantity" for the existing "ticker"
        update_query = "UPDATE stock_table SET Exchange = ?, Quantity = ? WHERE Ticker = ?"
        
        # Prepare the data for the update query, which includes the new "exchange", "quantity", and the existing "ticker"
        data = (exchange, quantity, ticker)
        
         # Execute the update query with the data to update the row for the existing "ticker"
        cursor.execute(update_query, data)
    else:
        # If the "ticker" does not exist in the "stock_table", define the SQL query to insert a new row with the provided data
        insert_query = "INSERT INTO stock_table (Ticker, Exchange, Quantity) VALUES (?, ?, ?)"
        
        # Prepare the data for the insert query, which includes the new "ticker", "exchange", and "quantity"
        data = (ticker, exchange, quantity)
        
        # Execute the insert query with the data to add a new row with the provided values
        cursor.execute(insert_query, data)
    
    # Commit the changes to the database to make them permanent    
    conn.commit()
    
    # Close the database connection to release resources
    conn.close()

# Function to fetch data from the SQLite database
def fetch_data():
    conn = sqlite3.connect("my_stocks_db.db")
    cursor = conn.cursor()

    select_query = "SELECT * FROM stock_table"
    cursor.execute(select_query)

    rows = cursor.fetchall()
    conn.close()
    return rows


# Defining the Stock class
@dataclass
class Stock:
    ticker: str
    exchange: str
    price: float = 0
    currency: str = "USD"
    usd_price: float = 0
    
    # def __post_init__(self):
    #     price_info = get_price_info(self.ticker, self.exchange)
    #     if price_info['ticker'] == self.ticker:
    #         self.price = price_info['price']
    #         self.currency = price_info['currency']
    #         self.usd_price = price_info['usd_price']

# Defining the Position class
@dataclass        
class Position:
    stock: Stock
    quantity: int

# Defining the Portfolio class
@dataclass        
class Portfolio:
    position: list[Position]
    # position: list
    
    def get_total_value(self):
        total_value = 0
        
        for position in self.position:
            total_value += position.quantity * position.stock.usd_price
            
        return total_value

# Function to display a summary of the portfolio        
def display_portfolio_summary(portfolio):
    
    # Check if the input 'portfolio' is an instance of the 'Portfolio' class
    if not isinstance(portfolio, Portfolio):
        raise TypeError("Please provide an instance of the Portfolio type")
    
    # Get the total value of the portfolio using the 'get_total_value()' method of the 'Portfolio' class
    portfolio_value =  portfolio.get_total_value()
    position_data = []
    
     # Iterate through the positions in the 'portfolio', sorted based on the market value (quantity * USD price) in descending order
    for position in sorted(portfolio.position,
                           key=lambda x: x.quantity * x.stock.usd_price,
                           reverse=True):
        position_data.append([
             # Append a list containing the summary data of the current position to the 'position_data' list
            position.stock.ticker,
            position.stock.exchange,
            position.quantity,
            position.stock.usd_price,
            position.quantity * position.stock.usd_price,
            position.quantity * position.stock.usd_price / portfolio_value * 100
        ])
        
    # Display the summary data in a tabular format using 'tabulate' library with 'psql' style and floating-point number formatting with two decimal places
    print(tabulate(position_data, 
                   headers=["Ticker", "Exchange", "Quantity (Units)", "Price ($)", "Market Value ($)", "% Allocation"], 
                   tablefmt="psql", 
                   floatfmt=".2f"))
    
    # Display the total value of the portfolio in USD with comma as thousands separator and two decimal places
    print(f"Total Portfolio value: ${portfolio_value:,.2f}.")
        
parent_url = "https://www.google.com/finance/quote" 

# Function to convert currency to USD using an external API
def convert_to_usd(currency):
    response = r.get(f"{parent_url}/{currency}-USD")
    soup = BeautifulSoup(response.content, "html.parser")
    fx_rate = soup.find("div", attrs={"data-last-price": True})
    fx = float(fx_rate['data-last-price'])
    return fx

# Function definition to retrieve price information for a given stock ticker and exchange
def get_price_info(ticker, exchange):
    try:
        response = r.get(f"{parent_url}/{ticker}:{exchange}")
        soup = BeautifulSoup(response.content, "html.parser")
        
        # It advise to from sections where data is most likely to be static than dynamic
        price_div = soup.find("div", attrs={"data-last-price": True})
        price = float(price_div['data-last-price'])
        currency = price_div['data-currency-code']
        
        usd_price = price
        # If the currency is not USD, convert the price to USD using the 'convert_to_usd' function
        if currency != "USD":
            fx = convert_to_usd(currency)
            usd_price = round(price * fx, 2)
        
        # Return a dictionary containing the stock information: ticker, exchange, price, currency, and USD price
        return {
            "ticker" : ticker,
            "exchange" : exchange,
            "price" : price,
            "currency" : currency,
            "usd_price" : usd_price
        }
    except Exception as e:
        # If an error occurs during the process, return an error message indicating a network error
        return f"Failed to load data from {parent_url}/{ticker}:{exchange} due to network error please try again!!!"
        

def welcome_message():
    print("""
              ............. STOCK PORTFOLIO TRACKER ..............
              
              Track you Stock Portfolio with ease.
              Let's Begin!
              
              Notice: All price values are expressed in USD.
            -----------------------------------------------------------------  
              """)
    
def prompt_message():
    print("""
            ............. What will you like todo? .............
            Press 1 to CREATE/UPDATE Portfolio
            Press 2 to VIEW existing Portfolio
            Press any other key to quit. 
          """)
    
def update_message():
    print("""
              Your stock portfolio has been updated successfully....
              
              Click Y to add another Stock to your Portfolio
                    OR
              Click N to continue
              """)

# Function definition for updating the portfolio with new stock information    
def update_portfolio():
    # Set the variable 'stocking' to True to enter the loop
    stocking = True
    
    # Continue looping until 'stocking' becomes False
    while stocking:
        print("........................ Add a Stock .......................")
        ticker_symbol = input("Input Ticker symbol: ").upper()
        exchange_symbol = input("Input Exchange symbol: ").upper()
        quantity = ''
        
        # Validate the user input for quantity to ensure it is an integer
        while type(quantity) != int:
            try:
                quantity = int(input("Input quantity in holdings (Integer only): "))
            except:
                print("Quantity should be an integer (Numbers)")
        
        # Display the details of the new stock to be added to the portfolio    
        print(f"""
              You just created a new stock with the details below:
                        Ticker Symbol: {ticker_symbol}
                        Exchange: {exchange_symbol}
                        Quantity: {quantity} units
                        
                Updating your Portfolio..............
              """)
        
        # Store the new stock data into the Database using the 'my_db' function
        my_db(ticker_symbol, exchange_symbol, quantity)
        
        time.sleep(3) 
                  
        # Prompt the user with a message to ask if they want to add more stocks           
        update_message()
        answer = input(": ")
        
        # If the user's answer is 'N' (No), set 'stocking' to False to exit the loop
        if answer.upper() == "N":
            stocking = False
            
# Function definition to view the portfolio
def view_portfolio():
    list_of_positions = []
    
    # Fetch data from the database using the 'fetch_data' function
    fetched_data = fetch_data()
    
     # Iterate through the fetched data to create Stock objects and Position objects
    for row in fetched_data:
        
        # Create a new Stock object with the 'ticker' and 'exchange' values from the fetched data
        new_stock = Stock(row[0], row[1])
        ticker_symbol = new_stock.ticker
        exchange_symbol = new_stock.exchange
        
        # Get price information for the stock using the 'get_price_info' function
        new_price_info = get_price_info(ticker_symbol, exchange_symbol)
        
        # Create a new Stock object with updated price and USD price information
        stock = Stock(row[0], row[1])
        stock = Stock(row[0], row[1])
        stock.price = new_price_info["price"]
        stock.ticker = new_price_info["ticker"]
        stock.usd_price = new_price_info["usd_price"]

        # Create a new Position object with the Stock object and the 'quantity' value from the fetched data
        position = Position(stock, row[2])
        list_of_positions.append(position)
    
    # Create a Portfolio object with the list of positions
    portfolio = Portfolio(list_of_positions)
    
    # Display Portfolio
    display_portfolio_summary(portfolio)



if __name__ == "__main__":
    welcome_message()
    time.sleep(2)
    
    prompt_message()
    try:
        prompt = int(input(""))
        if prompt not in (1, 2):
            exit()
        else:
            if prompt == 1:
                update_portfolio()
            else:
                view_portfolio()
    except:
        print("Network Error!!! Check your network connection & Try Again.....")
        exit()
    