"""
Description: This functions file contains all the functions related to the application, such as reading and writing csv files, 
applying formats, filtering data, etc.

Version: {config.APP_VERSION}     | Date: {config.APP_DATE}
"""
import pandas as pd # type: ignore
import numpy as np # type: ignore
import config
from datetime import datetime, date, timedelta
from pathlib import Path


def app_init():
    """
    Description: Reads all the needed information for the application.
    Input: N/A
    Output: tuple of needed data frames --> return importing_data, data
    """
    # import csv data
    importing_exp_path = get_path("importing_expenses")
    exp_path = get_path("expenses")
    categories_path = get_path("categories")
    accounts_path = get_path("accounts")
    account_history_path = get_path("accounts_history")
    
    importing_data = import_csv_data(importing_exp_path)
    data = import_csv_data(exp_path)
    categories_data = import_csv_data(categories_path)
    accounts_data = import_csv_data(accounts_path)
    account_history_data = import_csv_data(account_history_path)
    
    # apply needed format to data frames
    importing_data = apply_csv_format(importing_data)
    data= apply_csv_format(data)
    categories, subcategories = filter_categories(categories_data)
    
    # state memory to false
    config.state_memory = False
    
    return importing_data, data, categories, subcategories, accounts_data, account_history_data
  
  
def import_csv_data(csv_path):

    """
    Description: Reads the input csv and puts the info in the needed structure.
    Input: csv path (str)
    Output: csv (pandas data frame) 
    """
    # 2. Existence Check
    if not Path(csv_path).exists():
        print(f"{datetime.now()} DEBUG - File not found at: {csv_path}")
        return None

    try:
        # sep=None + engine='python' allows auto-detection of commas (,) or semicolons (;)
        data = pd.read_csv(csv_path, sep=None, engine='python', encoding='utf-8', parse_dates=['Fecha'], dayfirst=True)
        print(f"{datetime.now()} DEBUG - Readed CSV result: \n{data}")
        return data

    except Exception as e:
        try:
            # sep=None + engine='python' allows auto-detection of commas (,) or semicolons (;)
            data = pd.read_csv(csv_path, sep=None, engine='python', encoding='utf-8')
            print(f"{datetime.now()} DEBUG - Readed CSV result: \n{data}")
            return data
        except:
            print(f"{datetime.now()} DEBUG - Error processing the CSV: {e}")
            return None
  
  
def save_csv_data(df, path):
    df.to_csv(path, index=False)
   
   
def apply_csv_format(df):
    """
    Description: Applies the needed format for each column of the dataframe. Non parametriced, only for expenses csv.
    Input: csv (pandas data frame)
    Output: modified csv (pandas data frame) 
    """
    # Return if csv is empty
    if df is None:
        print(f"{datetime.now()} DEBUG - non existing csv.")
        return
        
    # Convert column type at dataframe
    df = df.astype({
        "Key": int,
        "Concepto": str,
        "Cuenta": str,
        "Importe": float,
        "Etiqueta 1": str,
        "Etiqueta 2": str,
        "Comentario": str,
    })
    
    print(f"{datetime.now()} DEBUG - Correct format applied to csv.")
    return df
  
  
def filter_categories(df):
    """
    Description: Separates the Categories and Subcategories in different lists. The common key to operate with will be the index.
    Input: csv (pandas data frame)
    Output: categories (array), subcategories (array)
    """
    # List init
    categories = []
    subcategories = []
    allsubcategories = []
    
    # Return if csv is empty
    if df is None:
        print(f"{datetime.now()} DEBUG - non existing csv.")
        return
        
    # Read the categories of the csv and apply to list
    categories = df["Cat"].dropna().unique().tolist()
    
    # Read subcategories and apply to list
    for row in range(len(df)):
        row_no_first_col = df.iloc[row, 1:].dropna()
        row_list = row_no_first_col.tolist()
        for item in row_list:
            subcategories.append(item)
            
    print(f"{datetime.now()} DEBUG - Categories list --> {categories}")
    print(f"{datetime.now()} DEBUG - Subcategories list --> {subcategories}")
    
    return categories, subcategories 
  
  
def get_path(file):
    """
    Description: Returns the absolute path of the file you search (as input)
    Input: Name of searching file --> "expenses" / "importing_expenses" / "categories" / "accounts"
    Output: full path (str)
    """
    
    # read hole application path and put the pointer at the initial folder
    base_path = str(Path(__file__).resolve().parent.parent) # Reading file complete path
    
    match file:
        case "expenses":
            absolute_path = base_path + config.EXP_PATH
        case "importing_expenses":
            absolute_path = base_path + config.IMPORTING_EXP_PATH
        case "categories":
            absolute_path = base_path + config.CATEGORIES_PATH 
        case "accounts":
            absolute_path = base_path + config.ACCOUNTS_PATH
        case "accounts_history":
            absolute_path = base_path + config.ACCOUNTS_HISTORY_PATH
        case _: 
            print(f"{datetime.now()} DEBUG - There is no configured path for {file} input.")
            return
            
    print(f"{datetime.now()} DEBUG - {file} CSV path succesfully got: {absolute_path}")
    return absolute_path
    

def get_metrics(df, initial_date, end_date, category, subcategory, comment):
    """
    Description: Calculates the total spent / income and balance from expenses df
    Input: expenses data frame and filter inputs
    Output: spent (int) / income (int) / balance (int)
    """
    # apply filters
    # 1. filer by date
    initial_date = pd.to_datetime(initial_date)
    end_date = pd.to_datetime(end_date)
    df = df[df['Fecha'].between(initial_date, end_date)]
    
    # calculate
    total_spents = df[df['Importe'] < 0]['Importe'].sum()
    total_incomes = df[df['Importe'] > 0]['Importe'].sum()
    balance = total_incomes + total_spents
    
    print(f"{datetime.now()} DEBUG - total spents --> {total_spents}")
    print(f"{datetime.now()} DEBUG - total incomes --> {total_incomes}")
    print(f"{datetime.now()} DEBUG - balance --> {balance}")
    
    return total_spents, total_incomes, balance
    

def import_revolut(uploader_output):
    """
    Description: Reads and returns the imported csv values. Returns error if format is not the specific.
    Input: uploader specified csv
    Output: dataframe with correct format
    """
    # Reading csv
    if uploader_output is not None:
        # import bank file
        importing_data = pd.read_csv(uploader_output)
        print(f"{datetime.now()} DEBUG - Importing csv readed:")
        print(importing_data)
        
        # import expense's csv formart (headers)
        importing_exp_path = get_path("importing_expenses")
        formated_importing_data = import_csv_data(importing_exp_path)
        
        # copy importing data into formated data frame
        formated_importing_data[['Concepto', 'Fecha', 'Importe']] = importing_data[['Descripción', 'Fecha de inicio', 'Importe']]
        formated_importing_data['Fecha'] = pd.to_datetime(formated_importing_data['Fecha'], format='mixed', dayfirst=True)
        print(f"{datetime.now()} DEBUG - Formatted data:")
        print(formated_importing_data)
        
        return formated_importing_data
        
    # Show error if csv does not exist    
    else:
        print(f"{datetime.now()} DEBUG - Error uploading selected csv. No csv selected. The uploader_output is --> {uploader_output}")
       

def import_caja_rural(uploader_output):
    """
    Description: Reads and returns the imported excel values. Returns error if format is not the specific.
    Input: uploader specified excel
    Output: dataframe with correct format
    """
    # Reading excel
    if uploader_output is not None:
        # import bank file
        importing_data = pd.read_excel(uploader_output,skiprows=3)
        print(f"{datetime.now()} DEBUG - Importing excel readed:")
        print(importing_data)
        
        # import expense's csv formart (headers)
        importing_exp_path = get_path("importing_expenses")
        formated_importing_data = import_csv_data(importing_exp_path)
        
        # copy importing data into formated data frame
        formated_importing_data[['Concepto', 'Fecha', 'Importe']] = importing_data[['Tipo movimiento', 'Fecha de la operación', 'Importe']]
        formated_importing_data['Fecha'] = pd.to_datetime(formated_importing_data['Fecha'], format='mixed', dayfirst=True)
        print(f"{datetime.now()} DEBUG - Formatted data:")
        print(formated_importing_data)
        
        return formated_importing_data
        
    # Show error if csv does not exist    
    else:
        print(f"{datetime.now()} DEBUG - Error uploading selected csv. No csv selected. The uploader_output is --> {uploader_output}")
       
def autofill(data, importing_csv):
    """
    Description: Applies the last used comment and labbels to importing csv rows. Always based on the last value applied to the Description.
    Input: data (Pandas df) as expenses dataframe, importing_csv (Pandas df)
    Output: filled importing_csv (Pandas df)
    """
    
    # Create the applying values df
    applying_values = data[['Concepto', 'Etiqueta 1', 'Etiqueta 2', 'Comentario']].drop_duplicates(
    subset=['Concepto'], 
    keep='last'
    )
    
    # Data merge
    importing_csv = importing_csv.drop(['Etiqueta 1', 'Etiqueta 2', 'Comentario'], axis=1) # Deleting the columns which will be merged
    importing_csv = importing_csv.merge(
    applying_values, 
    on='Concepto', 
    how='left'
    )
    
    # Key value application
    # Search of the current last key
    last_key = data['Key'].max()
    last_key = 0 if pd.isna(last_key) else int(last_key)
    
    # Calculation of new row quantity
    new_rows_value = len(importing_csv)

    # Incremental key value
    importing_csv['Key'] = range(last_key + 1, last_key + 1 + new_rows_value)
    
    return importing_csv
    
 
def get_account_name_list():
    """
    Description: Reads the configured account names in the project and returns them.
    Input: N/A
    Output: List of account names
    """
    csv_data = import_csv_data(get_path("accounts"))
    print(f"{datetime.now()} DEBUG - Account name csv data is --> {csv_data}")
    return list(csv_data["name"])
        
        
def generate_account_history():
    """
    Description: Generates a history dataframe per account which will show the account total value at each imported day.
    Input: N/A
    Output: Account history dataframe
    """
    # Import necessary data account initial value
    accounts_path = get_path("accounts")
    accounts_data = import_csv_data(accounts_path)
    
    account_history_path = get_path("accounts_history")
    account_history_data = import_csv_data(account_history_path)
    account_history_data = account_history_data.iloc[0:0] # delete last data
    
    exp_path = get_path("expenses")
    data = import_csv_data(exp_path)
    
    # take the first expense date
    first_expense_date = data['Fecha'].min()
    first_expense_date = first_expense_date.date()
    
    # loop for each bankaccount
    bankaccounts = accounts_data["name"].tolist()
    print(f" DEBUG - Bank accounts to generate history --> {bankaccounts}")
    i = 0
    for account in bankaccounts: 
        amount = accounts_data.loc[accounts_data['name'] == account, 'import'].values[0]
        account_history_data = account_history_data.iloc[0:0] # delete last data
        
        # filter data frame
        accountdata = data[data['Cuenta'] == account].copy()
        accountdata['Fecha'] = pd.to_datetime(accountdata['Fecha']) 
        accountdata = accountdata.sort_values(by='Fecha', ascending=True) # last dates at the start
            
        # Carge all the expenses with the specific amount
        for row in accountdata.itertuples():
            amount = row.Importe + amount
            amount = round(amount,2)
            new_row = {"account": account,"date":row.Fecha,"amount":amount}
            new_row = pd.DataFrame([new_row])
            account_history_data = pd.concat([account_history_data, new_row], ignore_index=True)
        
        # Resume the amounts by day
        if i == 0:
            filtered_account_history_data = account_history_data.copy()
            filtered_account_history_data = filtered_account_history_data.iloc[0:0] # delete last data
            # print(f"{datetime.now()} DEBUG - DataFrame deleted in i = {i}")
                
        ii = 0
        for row in account_history_data.itertuples():
            print(f"{datetime.now()} DEBUG - iteration nº {ii} in {row.account}")
            if ii == 0:
                amount = row.amount
                date = row.date
                date = date.date()
            else:
                new_date = row.date
                new_date = new_date.date()
                if date == new_date:
                    # print(f"{datetime.now()} DEBUG - Same date as before detected {date}")
                    amount = amount + (row.amount - amount)
                else:
                    # Saving previous data
                    amount = round(amount,2)
                    new_row = {"account": account,"date":date,"amount":amount}
                    new_row = pd.DataFrame([new_row])
                    filtered_account_history_data = pd.concat([filtered_account_history_data, new_row], ignore_index=True)
                        
                    # Preparing next row with new data
                    amount = amount + (row.amount - amount)
                    date = row.date
                    date = date.date()                    
            ii = ii + 1
        
        if ii == 0:
            # Saving bank account initial value if there are not expenses
            amount = round(amount, 2)
            new_row = {"account": account,"date":first_expense_date,"amount":amount}
            new_row = pd.DataFrame([new_row])
            filtered_account_history_data = pd.concat([filtered_account_history_data, new_row], ignore_index=True)
        else:  
            # Saving last data
            amount = round(amount, 2)
            new_row = {"account": account,"date":date,"amount":amount}
            new_row = pd.DataFrame([new_row])
            filtered_account_history_data = pd.concat([filtered_account_history_data, new_row], ignore_index=True)
        
        i = i + 1
        
    filtered_account_history_data = filtered_account_history_data.sort_values(by='date', ascending=True) # last dates at the start  

    # apply amount values for all the days between the last and the first date
    dayly_account_history_data = filtered_account_history_data.copy()
    dayly_account_history_data = dayly_account_history_data.iloc[0:0] # delete last data

    first_day = filtered_account_history_data["date"].min()
    last_day = filtered_account_history_data["date"].max()
    day_distance = (last_day - first_day).days

    #print(f"{datetime.now()} DEBUG - min date {first_day}")
    #print(f"{datetime.now()} DEBUG - min date {last_day}")
    #print(f"{datetime.now()} DEBUG - day distance {day_distance}")
    
    for account in bankaccounts: # travelling every day to insert the needed amount
        today = first_day
        last_amount = 0
        # print(f"{datetime.now()} DEBUG - Starting account: {account}")
        for days in range(day_distance+1):
            # print(f"{datetime.now()} DEBUG - Working at day {today}")
            row = filtered_account_history_data[(filtered_account_history_data['date'] == today) & (filtered_account_history_data['account'] == account)]
            try:
                last_amount = row.iloc[0]['amount']
            except IndexError:
                pass
            
            new_row = {"account": account,"date":today,"amount":last_amount}
            new_row = pd.DataFrame([new_row])
            dayly_account_history_data = pd.concat([dayly_account_history_data, new_row], ignore_index=True)

            today = timedelta(days=1) + today
        
    dayly_account_history_data = dayly_account_history_data.sort_values(by='date', ascending=True) # last dates at the start
    #print(f"{datetime.now()} DEBUG - New account history data: {dayly_account_history_data}")

    save_csv_data(dayly_account_history_data, account_history_path)


def import_trade_republic(pdf_path):
    import pdfplumber # type: ignore
    import re # type: ignore

    day_list = [
    {"label": "01 ene", "fecha": "2024-01-01"},
    {"label": "02 ene", "fecha": "2024-01-02"},
    {"label": "03 ene", "fecha": "2024-01-03"},
    {"label": "04 ene", "fecha": "2024-01-04"},
    {"label": "05 ene", "fecha": "2024-01-05"},
    {"label": "06 ene", "fecha": "2024-01-06"},
    {"label": "07 ene", "fecha": "2024-01-07"},
    {"label": "08 ene", "fecha": "2024-01-08"},
    {"label": "09 ene", "fecha": "2024-01-09"},
    {"label": "10 ene", "fecha": "2024-01-10"},
    {"label": "11 ene", "fecha": "2024-01-11"},
    {"label": "12 ene", "fecha": "2024-01-12"},
    {"label": "13 ene", "fecha": "2024-01-13"},
    {"label": "14 ene", "fecha": "2024-01-14"},
    {"label": "15 ene", "fecha": "2024-01-15"},
    {"label": "16 ene", "fecha": "2024-01-16"},
    {"label": "17 ene", "fecha": "2024-01-17"},
    {"label": "18 ene", "fecha": "2024-01-18"},
    {"label": "19 ene", "fecha": "2024-01-19"},
    {"label": "20 ene", "fecha": "2024-01-20"},
    {"label": "21 ene", "fecha": "2024-01-21"},
    {"label": "22 ene", "fecha": "2024-01-22"},
    {"label": "23 ene", "fecha": "2024-01-23"},
    {"label": "24 ene", "fecha": "2024-01-24"},
    {"label": "25 ene", "fecha": "2024-01-25"},
    {"label": "26 ene", "fecha": "2024-01-26"},
    {"label": "27 ene", "fecha": "2024-01-27"},
    {"label": "28 ene", "fecha": "2024-01-28"},
    {"label": "29 ene", "fecha": "2024-01-29"},
    {"label": "30 ene", "fecha": "2024-01-30"},
    {"label": "31 ene", "fecha": "2024-01-31"},
    {"label": "01 feb", "fecha": "2024-02-01"},
    {"label": "02 feb", "fecha": "2024-02-02"},
    {"label": "03 feb", "fecha": "2024-02-03"},
    {"label": "04 feb", "fecha": "2024-02-04"},
    {"label": "05 feb", "fecha": "2024-02-05"},
    {"label": "06 feb", "fecha": "2024-02-06"},
    {"label": "07 feb", "fecha": "2024-02-07"},
    {"label": "08 feb", "fecha": "2024-02-08"},
    {"label": "09 feb", "fecha": "2024-02-09"},
    {"label": "10 feb", "fecha": "2024-02-10"},
    {"label": "11 feb", "fecha": "2024-02-11"},
    {"label": "12 feb", "fecha": "2024-02-12"},
    {"label": "13 feb", "fecha": "2024-02-13"},
    {"label": "14 feb", "fecha": "2024-02-14"},
    {"label": "15 feb", "fecha": "2024-02-15"},
    {"label": "16 feb", "fecha": "2024-02-16"},
    {"label": "17 feb", "fecha": "2024-02-17"},
    {"label": "18 feb", "fecha": "2024-02-18"},
    {"label": "19 feb", "fecha": "2024-02-19"},
    {"label": "20 feb", "fecha": "2024-02-20"},
    {"label": "21 feb", "fecha": "2024-02-21"},
    {"label": "22 feb", "fecha": "2024-02-22"},
    {"label": "23 feb", "fecha": "2024-02-23"},
    {"label": "24 feb", "fecha": "2024-02-24"},
    {"label": "25 feb", "fecha": "2024-02-25"},
    {"label": "26 feb", "fecha": "2024-02-26"},
    {"label": "27 feb", "fecha": "2024-02-27"},
    {"label": "28 feb", "fecha": "2024-02-28"},
    {"label": "29 feb", "fecha": "2024-02-29"},
    {"label": "01 mar", "fecha": "2024-03-01"},
    {"label": "02 mar", "fecha": "2024-03-02"},
    {"label": "03 mar", "fecha": "2024-03-03"},
    {"label": "04 mar", "fecha": "2024-03-04"},
    {"label": "05 mar", "fecha": "2024-03-05"},
    {"label": "06 mar", "fecha": "2024-03-06"},
    {"label": "07 mar", "fecha": "2024-03-07"},
    {"label": "08 mar", "fecha": "2024-03-08"},
    {"label": "09 mar", "fecha": "2024-03-09"},
    {"label": "10 mar", "fecha": "2024-03-10"},
    {"label": "11 mar", "fecha": "2024-03-11"},
    {"label": "12 mar", "fecha": "2024-03-12"},
    {"label": "13 mar", "fecha": "2024-03-13"},
    {"label": "14 mar", "fecha": "2024-03-14"},
    {"label": "15 mar", "fecha": "2024-03-15"},
    {"label": "16 mar", "fecha": "2024-03-16"},
    {"label": "17 mar", "fecha": "2024-03-17"},
    {"label": "18 mar", "fecha": "2024-03-18"},
    {"label": "19 mar", "fecha": "2024-03-19"},
    {"label": "20 mar", "fecha": "2024-03-20"},
    {"label": "21 mar", "fecha": "2024-03-21"},
    {"label": "22 mar", "fecha": "2024-03-22"},
    {"label": "23 mar", "fecha": "2024-03-23"},
    {"label": "24 mar", "fecha": "2024-03-24"},
    {"label": "25 mar", "fecha": "2024-03-25"},
    {"label": "26 mar", "fecha": "2024-03-26"},
    {"label": "27 mar", "fecha": "2024-03-27"},
    {"label": "28 mar", "fecha": "2024-03-28"},
    {"label": "29 mar", "fecha": "2024-03-29"},
    {"label": "30 mar", "fecha": "2024-03-30"},
    {"label": "31 mar", "fecha": "2024-03-31"},
    {"label": "01 abr", "fecha": "2024-04-01"},
    {"label": "02 abr", "fecha": "2024-04-02"},
    {"label": "03 abr", "fecha": "2024-04-03"},
    {"label": "04 abr", "fecha": "2024-04-04"},
    {"label": "05 abr", "fecha": "2024-04-05"},
    {"label": "06 abr", "fecha": "2024-04-06"},
    {"label": "07 abr", "fecha": "2024-04-07"},
    {"label": "08 abr", "fecha": "2024-04-08"},
    {"label": "09 abr", "fecha": "2024-04-09"},
    {"label": "10 abr", "fecha": "2024-04-10"},
    {"label": "11 abr", "fecha": "2024-04-11"},
    {"label": "12 abr", "fecha": "2024-04-12"},
    {"label": "13 abr", "fecha": "2024-04-13"},
    {"label": "14 abr", "fecha": "2024-04-14"},
    {"label": "15 abr", "fecha": "2024-04-15"},
    {"label": "16 abr", "fecha": "2024-04-16"},
    {"label": "17 abr", "fecha": "2024-04-17"},
    {"label": "18 abr", "fecha": "2024-04-18"},
    {"label": "19 abr", "fecha": "2024-04-19"},
    {"label": "20 abr", "fecha": "2024-04-20"},
    {"label": "21 abr", "fecha": "2024-04-21"},
    {"label": "22 abr", "fecha": "2024-04-22"},
    {"label": "23 abr", "fecha": "2024-04-23"},
    {"label": "24 abr", "fecha": "2024-04-24"},
    {"label": "25 abr", "fecha": "2024-04-25"},
    {"label": "26 abr", "fecha": "2024-04-26"},
    {"label": "27 abr", "fecha": "2024-04-27"},
    {"label": "28 abr", "fecha": "2024-04-28"},
    {"label": "29 abr", "fecha": "2024-04-29"},
    {"label": "30 abr", "fecha": "2024-04-30"},
    {"label": "01 may", "fecha": "2024-05-01"},
    {"label": "02 may", "fecha": "2024-05-02"},
    {"label": "03 may", "fecha": "2024-05-03"},
    {"label": "04 may", "fecha": "2024-05-04"},
    {"label": "05 may", "fecha": "2024-05-05"},
    {"label": "06 may", "fecha": "2024-05-06"},
    {"label": "07 may", "fecha": "2024-05-07"},
    {"label": "08 may", "fecha": "2024-05-08"},
    {"label": "09 may", "fecha": "2024-05-09"},
    {"label": "10 may", "fecha": "2024-05-10"},
    {"label": "11 may", "fecha": "2024-05-11"},
    {"label": "12 may", "fecha": "2024-05-12"},
    {"label": "13 may", "fecha": "2024-05-13"},
    {"label": "14 may", "fecha": "2024-05-14"},
    {"label": "15 may", "fecha": "2024-05-15"},
    {"label": "16 may", "fecha": "2024-05-16"},
    {"label": "17 may", "fecha": "2024-05-17"},
    {"label": "18 may", "fecha": "2024-05-18"},
    {"label": "19 may", "fecha": "2024-05-19"},
    {"label": "20 may", "fecha": "2024-05-20"},
    {"label": "21 may", "fecha": "2024-05-21"},
    {"label": "22 may", "fecha": "2024-05-22"},
    {"label": "23 may", "fecha": "2024-05-23"},
    {"label": "24 may", "fecha": "2024-05-24"},
    {"label": "25 may", "fecha": "2024-05-25"},
    {"label": "26 may", "fecha": "2024-05-26"},
    {"label": "27 may", "fecha": "2024-05-27"},
    {"label": "28 may", "fecha": "2024-05-28"},
    {"label": "29 may", "fecha": "2024-05-29"},
    {"label": "30 may", "fecha": "2024-05-30"},
    {"label": "31 may", "fecha": "2024-05-31"},
    {"label": "01 jun", "fecha": "2024-06-01"},
    {"label": "02 jun", "fecha": "2024-06-02"},
    {"label": "03 jun", "fecha": "2024-06-03"},
    {"label": "04 jun", "fecha": "2024-06-04"},
    {"label": "05 jun", "fecha": "2024-06-05"},
    {"label": "06 jun", "fecha": "2024-06-06"},
    {"label": "07 jun", "fecha": "2024-06-07"},
    {"label": "08 jun", "fecha": "2024-06-08"},
    {"label": "09 jun", "fecha": "2024-06-09"},
    {"label": "10 jun", "fecha": "2024-06-10"},
    {"label": "11 jun", "fecha": "2024-06-11"},
    {"label": "12 jun", "fecha": "2024-06-12"},
    {"label": "13 jun", "fecha": "2024-06-13"},
    {"label": "14 jun", "fecha": "2024-06-14"},
    {"label": "15 jun", "fecha": "2024-06-15"},
    {"label": "16 jun", "fecha": "2024-06-16"},
    {"label": "17 jun", "fecha": "2024-06-17"},
    {"label": "18 jun", "fecha": "2024-06-18"},
    {"label": "19 jun", "fecha": "2024-06-19"},
    {"label": "20 jun", "fecha": "2024-06-20"},
    {"label": "21 jun", "fecha": "2024-06-21"},
    {"label": "22 jun", "fecha": "2024-06-22"},
    {"label": "23 jun", "fecha": "2024-06-23"},
    {"label": "24 jun", "fecha": "2024-06-24"},
    {"label": "25 jun", "fecha": "2024-06-25"},
    {"label": "26 jun", "fecha": "2024-06-26"},
    {"label": "27 jun", "fecha": "2024-06-27"},
    {"label": "28 jun", "fecha": "2024-06-28"},
    {"label": "29 jun", "fecha": "2024-06-29"},
    {"label": "30 jun", "fecha": "2024-06-30"},
    {"label": "01 jul", "fecha": "2024-07-01"},
    {"label": "02 jul", "fecha": "2024-07-02"},
    {"label": "03 jul", "fecha": "2024-07-03"},
    {"label": "04 jul", "fecha": "2024-07-04"},
    {"label": "05 jul", "fecha": "2024-07-05"},
    {"label": "06 jul", "fecha": "2024-07-06"},
    {"label": "07 jul", "fecha": "2024-07-07"},
    {"label": "08 jul", "fecha": "2024-07-08"},
    {"label": "09 jul", "fecha": "2024-07-09"},
    {"label": "10 jul", "fecha": "2024-07-10"},
    {"label": "11 jul", "fecha": "2024-07-11"},
    {"label": "12 jul", "fecha": "2024-07-12"},
    {"label": "13 jul", "fecha": "2024-07-13"},
    {"label": "14 jul", "fecha": "2024-07-14"},
    {"label": "15 jul", "fecha": "2024-07-15"},
    {"label": "16 jul", "fecha": "2024-07-16"},
    {"label": "17 jul", "fecha": "2024-07-17"},
    {"label": "18 jul", "fecha": "2024-07-18"},
    {"label": "19 jul", "fecha": "2024-07-19"},
    {"label": "20 jul", "fecha": "2024-07-20"},
    {"label": "21 jul", "fecha": "2024-07-21"},
    {"label": "22 jul", "fecha": "2024-07-22"},
    {"label": "23 jul", "fecha": "2024-07-23"},
    {"label": "24 jul", "fecha": "2024-07-24"},
    {"label": "25 jul", "fecha": "2024-07-25"},
    {"label": "26 jul", "fecha": "2024-07-26"},
    {"label": "27 jul", "fecha": "2024-07-27"},
    {"label": "28 jul", "fecha": "2024-07-28"},
    {"label": "29 jul", "fecha": "2024-07-29"},
    {"label": "30 jul", "fecha": "2024-07-30"},
    {"label": "31 jul", "fecha": "2024-07-31"},
    {"label": "01 ago", "fecha": "2024-08-01"},
    {"label": "02 ago", "fecha": "2024-08-02"},
    {"label": "03 ago", "fecha": "2024-08-03"},
    {"label": "04 ago", "fecha": "2024-08-04"},
    {"label": "05 ago", "fecha": "2024-08-05"},
    {"label": "06 ago", "fecha": "2024-08-06"},
    {"label": "07 ago", "fecha": "2024-08-07"},
    {"label": "08 ago", "fecha": "2024-08-08"},
    {"label": "09 ago", "fecha": "2024-08-09"},
    {"label": "10 ago", "fecha": "2024-08-10"},
    {"label": "11 ago", "fecha": "2024-08-11"},
    {"label": "12 ago", "fecha": "2024-08-12"},
    {"label": "13 ago", "fecha": "2024-08-13"},
    {"label": "14 ago", "fecha": "2024-08-14"},
    {"label": "15 ago", "fecha": "2024-08-15"},
    {"label": "16 ago", "fecha": "2024-08-16"},
    {"label": "17 ago", "fecha": "2024-08-17"},
    {"label": "18 ago", "fecha": "2024-08-18"},
    {"label": "19 ago", "fecha": "2024-08-19"},
    {"label": "20 ago", "fecha": "2024-08-20"},
    {"label": "21 ago", "fecha": "2024-08-21"},
    {"label": "22 ago", "fecha": "2024-08-22"},
    {"label": "23 ago", "fecha": "2024-08-23"},
    {"label": "24 ago", "fecha": "2024-08-24"},
    {"label": "25 ago", "fecha": "2024-08-25"},
    {"label": "26 ago", "fecha": "2024-08-26"},
    {"label": "27 ago", "fecha": "2024-08-27"},
    {"label": "28 ago", "fecha": "2024-08-28"},
    {"label": "29 ago", "fecha": "2024-08-29"},
    {"label": "30 ago", "fecha": "2024-08-30"},
    {"label": "31 ago", "fecha": "2024-08-31"},
    {"label": "01 sep", "fecha": "2024-09-01"},
    {"label": "02 sep", "fecha": "2024-09-02"},
    {"label": "03 sep", "fecha": "2024-09-03"},
    {"label": "04 sep", "fecha": "2024-09-04"},
    {"label": "05 sep", "fecha": "2024-09-05"},
    {"label": "06 sep", "fecha": "2024-09-06"},
    {"label": "07 sep", "fecha": "2024-09-07"},
    {"label": "08 sep", "fecha": "2024-09-08"},
    {"label": "09 sep", "fecha": "2024-09-09"},
    {"label": "10 sep", "fecha": "2024-09-10"},
    {"label": "11 sep", "fecha": "2024-09-11"},
    {"label": "12 sep", "fecha": "2024-09-12"},
    {"label": "13 sep", "fecha": "2024-09-13"},
    {"label": "14 sep", "fecha": "2024-09-14"},
    {"label": "15 sep", "fecha": "2024-09-15"},
    {"label": "16 sep", "fecha": "2024-09-16"},
    {"label": "17 sep", "fecha": "2024-09-17"},
    {"label": "18 sep", "fecha": "2024-09-18"},
    {"label": "19 sep", "fecha": "2024-09-19"},
    {"label": "20 sep", "fecha": "2024-09-20"},
    {"label": "21 sep", "fecha": "2024-09-21"},
    {"label": "22 sep", "fecha": "2024-09-22"},
    {"label": "23 sep", "fecha": "2024-09-23"},
    {"label": "24 sep", "fecha": "2024-09-24"},
    {"label": "25 sep", "fecha": "2024-09-25"},
    {"label": "26 sep", "fecha": "2024-09-26"},
    {"label": "27 sep", "fecha": "2024-09-27"},
    {"label": "28 sep", "fecha": "2024-09-28"},
    {"label": "29 sep", "fecha": "2024-09-29"},
    {"label": "30 sep", "fecha": "2024-09-30"},
    {"label": "01 oct", "fecha": "2024-10-01"},
    {"label": "02 oct", "fecha": "2024-10-02"},
    {"label": "03 oct", "fecha": "2024-10-03"},
    {"label": "04 oct", "fecha": "2024-10-04"},
    {"label": "05 oct", "fecha": "2024-10-05"},
    {"label": "06 oct", "fecha": "2024-10-06"},
    {"label": "07 oct", "fecha": "2024-10-07"},
    {"label": "08 oct", "fecha": "2024-10-08"},
    {"label": "09 oct", "fecha": "2024-10-09"},
    {"label": "10 oct", "fecha": "2024-10-10"},
    {"label": "11 oct", "fecha": "2024-10-11"},
    {"label": "12 oct", "fecha": "2024-10-12"},
    {"label": "13 oct", "fecha": "2024-10-13"},
    {"label": "14 oct", "fecha": "2024-10-14"},
    {"label": "15 oct", "fecha": "2024-10-15"},
    {"label": "16 oct", "fecha": "2024-10-16"},
    {"label": "17 oct", "fecha": "2024-10-17"},
    {"label": "18 oct", "fecha": "2024-10-18"},
    {"label": "19 oct", "fecha": "2024-10-19"},
    {"label": "20 oct", "fecha": "2024-10-20"},
    {"label": "21 oct", "fecha": "2024-10-21"},
    {"label": "22 oct", "fecha": "2024-10-22"},
    {"label": "23 oct", "fecha": "2024-10-23"},
    {"label": "24 oct", "fecha": "2024-10-24"},
    {"label": "25 oct", "fecha": "2024-10-25"},
    {"label": "26 oct", "fecha": "2024-10-26"},
    {"label": "27 oct", "fecha": "2024-10-27"},
    {"label": "28 oct", "fecha": "2024-10-28"},
    {"label": "29 oct", "fecha": "2024-10-29"},
    {"label": "30 oct", "fecha": "2024-10-30"},
    {"label": "31 oct", "fecha": "2024-10-31"},
    {"label": "01 nov", "fecha": "2024-11-01"},
    {"label": "02 nov", "fecha": "2024-11-02"},
    {"label": "03 nov", "fecha": "2024-11-03"},
    {"label": "04 nov", "fecha": "2024-11-04"},
    {"label": "05 nov", "fecha": "2024-11-05"},
    {"label": "06 nov", "fecha": "2024-11-06"},
    {"label": "07 nov", "fecha": "2024-11-07"},
    {"label": "08 nov", "fecha": "2024-11-08"},
    {"label": "09 nov", "fecha": "2024-11-09"},
    {"label": "10 nov", "fecha": "2024-11-10"},
    {"label": "11 nov", "fecha": "2024-11-11"},
    {"label": "12 nov", "fecha": "2024-11-12"},
    {"label": "13 nov", "fecha": "2024-11-13"},
    {"label": "14 nov", "fecha": "2024-11-14"},
    {"label": "15 nov", "fecha": "2024-11-15"},
    {"label": "16 nov", "fecha": "2024-11-16"},
    {"label": "17 nov", "fecha": "2024-11-17"},
    {"label": "18 nov", "fecha": "2024-11-18"},
    {"label": "19 nov", "fecha": "2024-11-19"},
    {"label": "20 nov", "fecha": "2024-11-20"},
    {"label": "21 nov", "fecha": "2024-11-21"},
    {"label": "22 nov", "fecha": "2024-11-22"},
    {"label": "23 nov", "fecha": "2024-11-23"},
    {"label": "24 nov", "fecha": "2024-11-24"},
    {"label": "25 nov", "fecha": "2024-11-25"},
    {"label": "26 nov", "fecha": "2024-11-26"},
    {"label": "27 nov", "fecha": "2024-11-27"},
    {"label": "28 nov", "fecha": "2024-11-28"},
    {"label": "29 nov", "fecha": "2024-11-29"},
    {"label": "30 nov", "fecha": "2024-11-30"},
    {"label": "01 dic", "fecha": "2024-12-01"},
    {"label": "02 dic", "fecha": "2024-12-02"},
    {"label": "03 dic", "fecha": "2024-12-03"},
    {"label": "04 dic", "fecha": "2024-12-04"},
    {"label": "05 dic", "fecha": "2024-12-05"},
    {"label": "06 dic", "fecha": "2024-12-06"},
    {"label": "07 dic", "fecha": "2024-12-07"},
    {"label": "08 dic", "fecha": "2024-12-08"},
    {"label": "09 dic", "fecha": "2024-12-09"},
    {"label": "10 dic", "fecha": "2024-12-10"},
    {"label": "11 dic", "fecha": "2024-12-11"},
    {"label": "12 dic", "fecha": "2024-12-12"},
    {"label": "13 dic", "fecha": "2024-12-13"},
    {"label": "14 dic", "fecha": "2024-12-14"},
    {"label": "15 dic", "fecha": "2024-12-15"},
    {"label": "16 dic", "fecha": "2024-12-16"},
    {"label": "17 dic", "fecha": "2024-12-17"},
    {"label": "18 dic", "fecha": "2024-12-18"},
    {"label": "19 dic", "fecha": "2024-12-19"},
    {"label": "20 dic", "fecha": "2024-12-20"},
    {"label": "21 dic", "fecha": "2024-12-21"},
    {"label": "22 dic", "fecha": "2024-12-22"},
    {"label": "23 dic", "fecha": "2024-12-23"},
    {"label": "24 dic", "fecha": "2024-12-24"},
    {"label": "25 dic", "fecha": "2024-12-25"},
    {"label": "26 dic", "fecha": "2024-12-26"},
    {"label": "27 dic", "fecha": "2024-12-27"},
    {"label": "28 dic", "fecha": "2024-12-28"},
    {"label": "29 dic", "fecha": "2024-12-29"},
    {"label": "30 dic", "fecha": "2024-12-30"},
    {"label": "31 dic", "fecha": "2024-12-31"},
]

    # import expense's csv formart (headers)
    importing_exp_path = get_path("importing_expenses")
    imported_data = import_csv_data(importing_exp_path)
    
    year = None
    expense_detected = False
    start_recording = False
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            print(f"{datetime.now()} DEBUG - The current page is: {page.page_number}")
            start_recording = False # reset the flag for the next page

            # extracting text with specific parameters to avoid errors in the date extraction
            text = page.extract_text(x_tolerance=3, x_tolerance_ratio=None, y_tolerance=3, layout=False, x_density=7.25, y_density=13, line_dir_render=None, char_dir_render=None)
            # spliting the text into lines to find the date line and extract the date from it
            lines = text.split('\n')
            # obtain the inporting expenses year from the start of the firts page
            if year is None:
                year = lines[1][-4:]
                
            for line in lines:
                if "DESCRIPCIÓN" in line:
                    start_recording = True
                elif "Creado en" in line:
                    start_recording = False

                if start_recording:
                    # if day detected the next line is the expense
                    if expense_detected:
                        if "CUENTAS COLECTIVAS SALDO" in line:
                            break # stop recording if the end of the expenses section is reached

                        print(f"{datetime.now()} DEBUG - The line with the expense is: {line}")
                        # Todo el texto hasta el primer número
                        texto = re.match(r'^([^\d]+)', line).group(1).strip()
                        # El primer número completo hasta el primer €
                        numero = re.search(r'([\d.,]+)\s*€', line).group(1)
                        numero = numero.replace(".", "").replace(",", ".") # Convertir a formato numérico
                        print(importing_row["Fecha"]) # "2024-01-30"
                        print(texto)   # "Transferencia"
                        print(numero)  # "30,00"
                        
                        importing_row["Concepto"] = texto
                        importing_row["Importe"] = numero    

                        expense_detected = False # reset the flag for the next expense
                        imported_data = pd.concat([imported_data, pd.DataFrame([importing_row])], ignore_index=True) # add the importing row to the imported data

                    # if the line contains the date, extract the date and add it to the importing data   
                    else:
                        for day in day_list:
                            if day["label"] in line:
                                print(f"{datetime.now()} DEBUG - The line with the date is: {line}")
                                print(f"{datetime.now()} DEBUG - The date extracted from the line is: {day['fecha']}")
                                expense_detected = True
                                date =year+day["fecha"][4:]  # add the year to the date
                                if imported_data.empty:
                                    importing_row = {"Concepto": date, "Fecha": None, "Importe": None}
                                else:
                                    importing_row = imported_data.iloc[0] 
                                importing_row["Fecha"] = date

                else:
                    pass # skip lines until the expense section is reached    

    imported_data["Importe"] = imported_data["Importe"].astype(float)
    imported_data["Fecha"] = pd.to_datetime(imported_data["Fecha"], format="%Y-%m-%d") 
    """
    for idx, i in imported_data.iterrows():
        print(f"{datetime.now()} DEBUG - The row is: {i}")
        if "null" in i["Concepto"].lower():
            imported_data.at[idx, "Importe"] = float(i["Importe"]) * -1
            imported_data.at[idx, "Concepto"] = i["Concepto"].replace("null", "").strip()
        else:
            imported_data.at[idx, "Importe"] = float(i["Importe"]) * 1
    """
    print(f"{datetime.now()} DEBUG - The final data is: {imported_data}") 
    return imported_data

       
    
