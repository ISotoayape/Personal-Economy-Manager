"""
Description: this functions file contains all the functions related to the application, such as reading and writing csv files,
applying formats, filtering data, etc.

Version: {config.APP_VERSION}     | Date: {config.APP_DATE}
"""
import calendar
import re
import pandas as pd # type: ignore
import numpy as np # type: ignore
import config
from datetime import datetime
from pathlib import Path


_MONTH_ABBR_ES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun',
                  'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

_PATHS = {
    "expenses":           config.EXP_PATH,
    "importing_expenses": config.IMPORTING_EXP_PATH,
    "categories":         config.CATEGORIES_PATH,
    "accounts":           config.ACCOUNTS_PATH,
    "accounts_history":   config.ACCOUNTS_HISTORY_PATH,
}


def app_init():
    importing_data       = import_csv_data(get_path("importing_expenses"))
    data                 = import_csv_data(get_path("expenses"))
    categories_data      = import_csv_data(get_path("categories"))
    accounts_data        = import_csv_data(get_path("accounts"))
    account_history_data = import_csv_data(get_path("accounts_history"))

    importing_data = apply_csv_format(importing_data)
    data           = apply_csv_format(data)
    categories, subcategories, excluded_categories = filter_categories(categories_data)

    config.state_memory = False

    return importing_data, data, categories, subcategories, accounts_data, account_history_data, excluded_categories


def import_csv_data(csv_path):
    if not Path(csv_path).exists():
        print(f"{datetime.now()} DEBUG - File not found at: {csv_path}")
        return None

    try:
        data = pd.read_csv(csv_path, sep=None, engine='python', encoding='utf-8',
                           parse_dates=['Fecha'], dayfirst=True)
        print(f"{datetime.now()} DEBUG - Readed CSV result: \n{data}")
        return data
    except Exception:
        try:
            data = pd.read_csv(csv_path, sep=None, engine='python', encoding='utf-8')
            print(f"{datetime.now()} DEBUG - Readed CSV result: \n{data}")
            return data
        except Exception as e:
            print(f"{datetime.now()} DEBUG - Error processing the CSV: {e}")
            return None


def save_csv_data(df, path):
    df.to_csv(path, index=False)


def apply_csv_format(df):
    if df is None:
        print(f"{datetime.now()} DEBUG - non existing csv.")
        return None

    df = df.astype({
        "Key":        int,
        "Concepto":   str,
        "Cuenta":     str,
        "Importe":    float,
        "Etiqueta 1": str,
        "Etiqueta 2": str,
        "Comentario": str,
    })

    print(f"{datetime.now()} DEBUG - Correct format applied to csv.")
    return df


def filter_categories(df):
    if df is None:
        print(f"{datetime.now()} DEBUG - non existing csv.")
        return [], [], []

    categories    = df["Cat"].dropna().unique().tolist()
    subcategories = df.drop(columns=['Cat', 'Excluir'], errors='ignore').stack().tolist()

    excluded_categories = []
    if 'Excluir' in df.columns:
        excluded_categories = df[df['Excluir'].astype(str).str.lower() == 'true']['Cat'].dropna().tolist()

    print(f"{datetime.now()} DEBUG - Categories list --> {categories}")
    print(f"{datetime.now()} DEBUG - Subcategories list --> {subcategories}")
    print(f"{datetime.now()} DEBUG - Excluded categories --> {excluded_categories}")
    return categories, subcategories, excluded_categories


def get_path(file):
    base_path = str(Path(__file__).resolve().parent.parent)
    path = _PATHS.get(file)
    if path is None:
        print(f"{datetime.now()} DEBUG - There is no configured path for {file} input.")
        return None
    absolute_path = base_path + path
    print(f"{datetime.now()} DEBUG - {file} CSV path succesfully got: {absolute_path}")
    return absolute_path


def get_metrics(df, initial_date, end_date, category, subcategory, comment):
    initial_date = pd.to_datetime(initial_date)
    end_date     = pd.to_datetime(end_date)
    df = df[df['Fecha'].between(initial_date, end_date)]

    total_spents  = df[df['Importe'] < 0]['Importe'].sum()
    total_incomes = df[df['Importe'] > 0]['Importe'].sum()
    balance       = total_incomes + total_spents

    print(f"{datetime.now()} DEBUG - total spents --> {total_spents}")
    print(f"{datetime.now()} DEBUG - total incomes --> {total_incomes}")
    print(f"{datetime.now()} DEBUG - balance --> {balance}")

    return total_spents, total_incomes, balance


def import_revolut(uploader_output):
    if uploader_output is None:
        print(f"{datetime.now()} DEBUG - Error: no csv selected.")
        return None

    importing_data        = pd.read_csv(uploader_output)
    formated_importing_data = import_csv_data(get_path("importing_expenses"))

    formated_importing_data[['Concepto', 'Fecha', 'Importe']] = importing_data[['Descripción', 'Fecha de inicio', 'Importe']]
    formated_importing_data['Fecha'] = pd.to_datetime(formated_importing_data['Fecha'], format='mixed', dayfirst=True)

    print(f"{datetime.now()} DEBUG - Formatted data:\n{formated_importing_data}")
    return formated_importing_data


def import_caja_rural(uploader_output):
    if uploader_output is None:
        print(f"{datetime.now()} DEBUG - Error: no excel selected.")
        return None

    importing_data          = pd.read_excel(uploader_output, skiprows=3)
    formated_importing_data = import_csv_data(get_path("importing_expenses"))

    formated_importing_data[['Concepto', 'Fecha', 'Importe']] = importing_data[['Tipo movimiento', 'Fecha de la operación', 'Importe']]
    formated_importing_data['Fecha'] = pd.to_datetime(formated_importing_data['Fecha'], format='mixed', dayfirst=True)

    print(f"{datetime.now()} DEBUG - Formatted data:\n{formated_importing_data}")
    return formated_importing_data


def autofill(data, importing_csv):
    applying_values = data[['Concepto', 'Etiqueta 1', 'Etiqueta 2', 'Comentario']].drop_duplicates(
        subset=['Concepto'], keep='last'
    )

    importing_csv = importing_csv.drop(['Etiqueta 1', 'Etiqueta 2', 'Comentario'], axis=1)
    importing_csv = importing_csv.merge(applying_values, on='Concepto', how='left')

    last_key = data['Key'].max()
    last_key = 0 if pd.isna(last_key) else int(last_key)
    importing_csv['Key'] = range(last_key + 1, last_key + 1 + len(importing_csv))

    return importing_csv


def get_account_name_list():
    csv_data = import_csv_data(get_path("accounts"))
    print(f"{datetime.now()} DEBUG - Account name csv data is --> {csv_data}")
    return list(csv_data["name"])


def generate_account_history():
    accounts_data = import_csv_data(get_path("accounts"))
    data          = import_csv_data(get_path("expenses"))

    data['Fecha'] = pd.to_datetime(data['Fecha'])
    first_day  = data['Fecha'].min().date()
    last_day   = data['Fecha'].max().date()
    date_range = pd.date_range(first_day, last_day, freq='D').date

    results = []
    for _, acct in accounts_data.iterrows():
        name    = acct['name']
        initial = float(acct['import'])

        acc_exp = data[data['Cuenta'] == name].sort_values('Fecha').copy()
        acc_exp['running'] = acc_exp['Importe'].cumsum() + initial
        acc_exp['day']     = acc_exp['Fecha'].dt.date

        # Keep last balance per day, then forward-fill across the full date range
        daily = acc_exp.groupby('day')['running'].last()
        daily = daily.reindex(date_range, method='ffill').fillna(initial).round(2)

        results.append(pd.DataFrame({'account': name, 'date': date_range, 'amount': daily.values}))

    result = pd.concat(results, ignore_index=True).sort_values('date')
    save_csv_data(result, get_path("accounts_history"))


def _build_trade_republic_day_list():
    days = []
    for month in range(1, 13):
        _, max_day = calendar.monthrange(2024, month)  # 2024 = leap year, covers Feb 29
        for day in range(1, max_day + 1):
            days.append({
                "label": f"{day:02d} {_MONTH_ABBR_ES[month - 1]}",
                "fecha": f"2024-{month:02d}-{day:02d}",
            })
    return days


def import_trade_republic(pdf_path):
    import pdfplumber # type: ignore

    day_list      = _build_trade_republic_day_list()
    imported_data = import_csv_data(get_path("importing_expenses"))

    year            = None
    expense_detected = False
    start_recording  = False
    importing_row    = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            print(f"{datetime.now()} DEBUG - The current page is: {page.page_number}")
            start_recording = False

            text  = page.extract_text(x_tolerance=3, x_tolerance_ratio=None, y_tolerance=3, layout=False,
                                      x_density=7.25, y_density=13, line_dir_render=None, char_dir_render=None)
            lines = text.split('\n')

            if year is None:
                year = lines[1][-4:]

            for line in lines:
                if "DESCRIPCIÓN" in line:
                    start_recording = True
                elif "Creado en" in line:
                    start_recording = False

                if not start_recording:
                    continue

                if expense_detected:
                    if "CUENTAS COLECTIVAS SALDO" in line:
                        break

                    print(f"{datetime.now()} DEBUG - Expense line: {line}")
                    texto  = re.match(r'^([^\d]+)', line).group(1).strip()
                    numero = re.search(r'([\d.,]+)\s*€', line).group(1)
                    numero = numero.replace(".", "").replace(",", ".")

                    importing_row["Concepto"] = texto
                    importing_row["Importe"]  = numero
                    expense_detected = False
                    imported_data = pd.concat([imported_data, pd.DataFrame([importing_row])], ignore_index=True)

                else:
                    for day in day_list:
                        if day["label"] in line:
                            print(f"{datetime.now()} DEBUG - Date detected: {day['fecha']}")
                            expense_detected = True
                            fecha = year + day["fecha"][4:]
                            if imported_data.empty:
                                importing_row = {"Concepto": None, "Fecha": None, "Importe": None}
                            else:
                                importing_row = imported_data.iloc[0].copy()
                            importing_row["Fecha"] = fecha
                            break

    imported_data["Importe"] = imported_data["Importe"].astype(float)
    imported_data["Fecha"]   = pd.to_datetime(imported_data["Fecha"], format="%Y-%m-%d")

    print(f"{datetime.now()} DEBUG - The final data is: {imported_data}")
    return imported_data
