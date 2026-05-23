"""
Description: this is the main file of the application, it contains the main function that runs the app and calls the main_gui function.

Version: {config.APP_VERSION}     | Date: {config.APP_DATE}
"""

# main.py
import os
from functions import app_init, save_csv_data, generate_account_history
from gui import main_gui
  
def main():
    generate_account_history() # generate account history from expenses and accounts data

    importing_data, data, categories, subcategories, accounts, accounts_history_data, excluded_categories = app_init() # csv reading and settup
    main_gui(importing_data, data, categories, subcategories, accounts, accounts_history_data, excluded_categories) # streamlit server
    
        
if __name__ == "__main__":
    main()