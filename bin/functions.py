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

    rows = []
    print(f"{datetime.now()} DEBUG - Starting pdf import with path: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        print(f"{datetime.now()} DEBUG - The pdf is: {pdf.pages[0]}")
        for page in pdf.pages:
            table= page.extract_table()
            print(f"{datetime.now()} DEBUG - The table extracted is: {table}")    
            text= page.extract_text()
            print(f"{datetime.now()} DEBUG - The text extracted is: {text}")
    
