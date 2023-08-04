# Stock Portfolio Tracker
The Stock Portfolio Tracker is a Python program that allows users to track their stock portfolio easily. It leverages SQLite to store and manage data related to the user's stocks. The program provides functionalities to create/update a portfolio and view an existing portfolio all using your COMMAND LINE INTERFACE.

### Prerequisites
Before running the Stock Portfolio Tracker, ensure that you have the necessary libraries installed. You can install them using the following commands:
. pip install requests
. pip install beautifulsoup4
. pip install dataclasses
. pip install tabulate

### Usage
Run the script to launch the Stock Portfolio Tracker.
The program will prompt you to select an action:
Press 1 to create/update the portfolio.
Press 2 to view the existing portfolio.
Press any other key to quit the program.
If you choose to create/update the portfolio, you will be prompted to input the ticker symbol, exchange symbol, and quantity of the stock you want to add. The program will update the database with the provided information.

If you choose to view the existing portfolio, the program will fetch the data from the database, retrieve the latest price information for each stock, calculate the portfolio value, and display a summary of the portfolio with relevant details.

### Note
Ensure you have a stable internet connection as the program may interact with external APIs to retrieve stock prices and currency exchange rates.

This documentation provides an overview of the Stock Portfolio Tracker and its functionalities. For more detailed information, please refer to the code comments and function definitions within the source code. Happy tracking!
