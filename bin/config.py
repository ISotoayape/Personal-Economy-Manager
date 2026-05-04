"""
Description: this is config file of the application, it contains all the constants and configuration variables that are used in the app.

Version: {config.APP_VERSION}     | Date: {config.APP_DATE}
"""

################################### APP info ###################################
APP_VERSION = "PEconomy 1.0.0"
APP_AUTHOR  = "Iker Soto "
APP_DATE    = "2026-04-26"

################################### APP ###################################
IMPORTING_EXP_PATH = "\\data\\importing_expenses.csv"
EXP_PATH = "\\data\\expenses.csv"
CATEGORIES_PATH = "\\data\\categories.csv"
ACCOUNTS_PATH = "\\data\\bankaccounts.csv"
ACCOUNTS_HISTORY_PATH = "\\data\\account_history.csv"
COMPATIBLE_BANKS = ["Revolut", "Caja Rural", "Trade Republic", "Imagin"]

################################### GUI CONFIGURATION ###################################
# --- PAGE CONFIGURATION ---
PG_TITLE="PEM" 
PG_ICON="z:\10_MIPC\10_MISSCRIPTS\PEconomy\bin\images\icon.png" # icon or image path NOTA: la path tiene que ser relativa.

# --- SIDEBAR ---
SB_TITLE="Personal Economy Manager"

# --- HOME ---
GRAPHIC_STYLE = 'dark_background'