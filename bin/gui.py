"""
Description: this gui file contains all the functions related to the graphical user interface of the application,
it uses streamlit library to create the interface and plotly for the graphics.

Version: {config.APP_VERSION}     | Date: {config.APP_DATE}
"""

import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import datetime
from datetime import datetime
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
import matplotlib.pyplot as plt # type: ignore


import config
from functions import save_csv_data, get_path, get_metrics, import_revolut, autofill, get_account_name_list, import_caja_rural, generate_account_history, import_trade_republic


def main_gui(importing_data, data, categories, subcategories, accounts, accounts_history_data):
    # --- PAGE CONFIGURATION ---
    st.set_page_config(
        page_title=config.PG_TITLE,
        page_icon=config.PG_ICON,
        layout="wide",
        initial_sidebar_state="expanded" # auto/expanded/collapsed
    )
    
    # First init 
    if "page" not in st.session_state:
        st.session_state.page = "HOME"
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.title(config.SB_TITLE)
        st.button("HOME",
                  help=None,
                  on_click=change_page,
                  args=["HOME"], #<-- Called function arguments
                  #kwargs={}, <-- Called function dictionary args
                  type="secondary", # primary/secondary <-- Changes button color to red
                  use_container_width="True",
                  key="bttn_home")
        st.button("EXPENSES",
                  help=None,
                  on_click=change_page,
                  args=["EXPENSES"], # <-- Called function arguments
                  #kwargs={}, <-- Called function dictionary args
                  type="secondary", # primary/secondary <-- Changes button color to red
                  use_container_width="True",
                  key="bttn_expenses")
        st.button("IMPORT",
                  help=None,
                  on_click=change_page,
                  args=["IMPORT"], #<-- Called function arguments
                  #kwargs={}, <-- Called function dictionary args
                  type="secondary", # primary/secondary <-- Changes button color to red
                  use_container_width="True",
                  key="bttn_import")
        st.button("EXPORT",
                  help=None,
                  on_click=change_page,
                  args=["EXPORT"], #<-- Called function arguments
                  #kwargs={}, <-- Called function dictionary args
                  type="secondary", # primary/secondary <-- Changes button color to red
                  use_container_width="True",
                  key="bttn_export")
        st.button("SETTINGS",
                  help=None,
                  on_click=change_page,
                  args=["SETTINGS"], #<-- Called function arguments
                  #kwargs={}, <-- Called function dictionary args
                  type="secondary", # primary/secondary <-- Changes button color to red
                  use_container_width="True",
                  key="bttn_settings")
        
    # --- LAST STATE ---
    if st.session_state.page == "HOME":
        show_home(data, categories, subcategories, accounts, accounts_history_data)
    elif st.session_state.page == "EXPENSES":
        show_expenses(data, categories, subcategories)
    elif st.session_state.page == "IMPORT":
        show_import(data, categories, subcategories, accounts)
    elif st.session_state.page == "EXPORT":
        show_export()
    elif st.session_state.page == "SETTINGS":
        show_settings()
    
################################################### PAGES ###################################################        
def show_home(data, categories, subcategories, accounts, accounts_history_data):
    # ---- MAIN PAGE ----
    # Page state 
    change_page('HOME')
    
    # --- HEADER ---
    st.title("DASHBOARD")
    
    # --- FILTERS ---
    if not data.empty:
        # Filter and button generation
        col_1, col_2, col_3 = st.columns(3)
        
        with col_1:
            selected_ini_date = st.date_input(
                                    label="Select initial date",
                                    value=data['Fecha'].min(),
                                    min_value=data['Fecha'].min(),
                                    max_value=data['Fecha'].max(),
                                    format="DD/MM/YYYY")
        with col_2:
            selected_end_date = st.date_input(
                                    label="Select end date",
                                    value=data['Fecha'].max(),
                                    min_value=data['Fecha'].min(),
                                    max_value=data['Fecha'].max(),
                                    format="DD/MM/YYYY")
        with col_3:
            accounts_list = data["Cuenta"].tolist()
            accounts_list = list(set(accounts_list))
            accounts_list = ["All"] + accounts_list            
            selected_account = st.selectbox("Account",accounts_list, key="filter_account")

        st.markdown("---") # separation line for next graph
        
        # --- BALANCE GRAPH + KPIS ---
        col_1, col_2 = st.columns([0.33, 0.67])
        with col_1:
            balance_graph(selected_ini_date, selected_end_date, selected_account, data)
        with col_2:
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            balance_kpis_and_table(selected_ini_date, selected_end_date, selected_account, accounts_history_data, data)
                 
        
        st.markdown("---") # separation line for next graph
        # --- VARIATION GRAPH ---
        variation_graph(selected_ini_date, selected_end_date, selected_account, accounts_history_data)

        st.markdown("---") # separation line for next graph
        # --- CATEGORIES' PIE GRAPHS ---
        col_1, col_2 = st.columns([0.6,0.4])
        with col_1:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            category_sunburst_graph(selected_ini_date, selected_end_date, selected_account, data)
        with col_2:
            st.markdown("#### KPIs")
            category_stats(selected_ini_date, selected_end_date, selected_account, data)

        st.markdown("---") # separation line for next graph
        # --- COMMENT SEARCHER ---
        col_1, col_2 = st.columns([0.6,0.4])
        with col_1:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.subheader("Comment searcher")
        with col_2:
            options = data['Comentario'].unique().tolist()
            selected = st.selectbox("Comment", options)
            
        if selected:
            filtered_data = data[data['Comentario'].str.contains(selected, case=False, na=False)]
            comments_kpi(data, filtered_data)
            st.dataframe(filtered_data[['Fecha', 'Concepto', 'Cuenta', 'Importe', 'Etiqueta 1', 'Etiqueta 2', 'Comentario']], 
                         use_container_width=True, 
                         height=38+(len(filtered_data)*38)-10) # 38px header + 38px per row (max 4 rows without scroll)
            
        app_footer()
        
    else:
        st.info("Please, import your first expenses ;)")
    
def show_expenses(data, categories, subcategories):
    # Page state 
    change_page('EXPENSES')
    
    st.title("Edición de Gastos")
    
    if not data.empty:
        # Configure expenses table
        st.session_state.expenses_df = pd.DataFrame(data)

        column_config = {
            "key": st.column_config.NumberColumn("ID", width="small", min_value = 0, required = True),
            "Concepto": st.column_config.TextColumn("Concepto", width="medium", required=True),
            "Fecha": st.column_config.DateColumn(
                "Fecha",
                format="DD/MM/YYYY",
                required=True
            ),
            "Cuenta": st.column_config.SelectboxColumn(
                "Cuenta",
                options=["Revolut", "Caja Rural", "Trade Republic"], # Nota: Pendiente preconfigurar en config
                required=True
            ),
            "Importe": st.column_config.NumberColumn(
                "Importe",
                format="%.2f €",
                # min_value=0, # No permite números negativos
                required=True
            ),
            "Etiqueta 1": st.column_config.SelectboxColumn(
                "Etiqueta 1",
                options=categories,
                required=True
            ),
            "Etiqueta 2": st.column_config.SelectboxColumn(
                "Etiqueta 2",
                options=subcategories,
                required=True
            ),
            "Comentario": st.column_config.TextColumn("Comentario", width="large"),
        }

                
        # El resultado se guarda directamente en una nueva variable 'edited_df'
        edited_df = st.data_editor(
            st.session_state.expenses_df,
            column_config=column_config,
            num_rows="dynamic",     # Permite al usuario añadir/borrar filas
            hide_index=True,
            use_container_width=True,
            height=725,
            key="dataeditor_expenses"    # Llave única para el estado del widget
        )

        # 4. Botón para guardar los cambios de forma permanente
        state = st.session_state.dataeditor_expenses
        
        # Si hay algo en editados, añadidos o borrados, activamos el botón
        if state["edited_rows"] or state["added_rows"] or state["deleted_rows"]:
            df_edited = True
        else:
            df_edited = False
            
        if st.button("Guardar Cambios", type="primary", disabled = not df_edited):
            # Actualizamos el DataFrame principal en la sesión
            st.session_state.expenses_df = edited_df

            save_csv_data(edited_df, get_path("expenses"))
            st.success("¡Datos actualizados y guardados correctamente!")
            # Forzamos un rerun para que la interfaz se actualice con los nuevos datos
            st.rerun()
        
        app_footer()

    else:
        st.info("Please, import your first expenses ;)")


def show_import(data, categories, subcategories, accounts):
    # ---- IMPORT PAGE ----
    # Page state 
    change_page('IMPORT')
    
    if 'import_process' not in st.session_state:
        st.session_state.import_process = False
        
    st.title("CSV IMPORT")
    
    # Filter and button generation
    col_1, col_2, col_3 = st.columns(3)
    
    importing_bank = None
    importing_csv = None
    
    with col_1:
        importing_bank = st.selectbox("Cuenta",config.COMPATIBLE_BANKS, key="filter_bank")
    with col_2:
        importing_csv = st.file_uploader(
            "Selecciona tu extracto bancario", 
            type=["csv","xlsx","pdf"],
            help="Arrastra aquí el fichero .csv exportado de tu banca online")
    with col_3:
        if importing_bank is not None and importing_csv is not None and not st.session_state.import_process:
            ready_to_import = True
        else:
            ready_to_import = False
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("IMPORT", use_container_width=True, type="primary", disabled = not ready_to_import):
            
            st.session_state.import_process = True
            match importing_bank:
                case "Revolut":
                    print(f"{datetime.now()} DEBUG - Revolut")
                    importing_df = import_revolut(importing_csv)
                    importing_df = autofill(data, importing_df)
                    st.session_state.importing_expenses = importing_df
                case "Caja Rural":
                    print(f"{datetime.now()} DEBUG - Caja Rural")
                    importing_df = import_caja_rural(importing_csv)
                    importing_df = autofill(data, importing_df)
                    st.session_state.importing_expenses = importing_df
                case "Trade Republic":
                    print(f"{datetime.now()} DEBUG - Trade Republic")
                    importing_df = import_trade_republic(importing_csv)
                    importing_df = autofill(data, importing_df)
                    st.session_state.importing_expenses = importing_df
                case "Imagin":
                    print(f"{datetime.now()} DEBUG - Imagin")
            st.rerun()
            
    st.markdown("---")
        
    if st.session_state.import_process:
        # Configure expenses table
        column_config = {
            "key": st.column_config.NumberColumn("ID", width="small", min_value = 0, required = True),
            "Concepto": st.column_config.TextColumn("Concepto", width="medium", required=True),
            "Fecha": st.column_config.DateColumn(
                "Fecha",
                format="DD/MM/YYYY",
                required=True
            ),
            "Cuenta": st.column_config.SelectboxColumn(
                "Cuenta",
                options=accounts['name'].tolist(),
                required=True
            ),
            "Importe": st.column_config.NumberColumn(
                "Importe",
                format="%.2f €",
                # min_value=0, # No permite números negativos
                required=True
            ),
            "Etiqueta 1": st.column_config.SelectboxColumn(
                "Etiqueta 1",
                options=categories,
                required=True
            ),
            "Etiqueta 2": st.column_config.SelectboxColumn(
                "Etiqueta 2",
                options=subcategories,
                required=True
            ),
            "Comentario": st.column_config.TextColumn("Comentario", width="large"),
        }
            
        # data editor writing
        importing_df = st.data_editor(
            st.session_state.importing_expenses,
            column_config=column_config,
            num_rows="dynamic",     # Permite al usuario añadir/borrar filas
            hide_index=True,
            use_container_width=True,
            height=500,
            key="dataeditor_importing_expenses"    # Llave única para el estado del widget
        )
        
        # Save & Cancel buttons     
        button_1, button_2, space = st.columns([0.15, 0.15, 0.7])
        with button_1: # Save button
            
            critical_columns = ['Key', 'Concepto', 'Fecha', 'Cuenta', 'Importe', 'Etiqueta 1', 'Etiqueta 2']
            not_ready = importing_df[critical_columns].isna().any().any()
            
            if st.button("Save", type="primary", use_container_width="True", disabled = not_ready):
                data = pd.concat([data, importing_df], axis=0, ignore_index=True)
                
                print(f"{datetime.now()} DEBUG - The new data frame is:")
                print(f"{data}")
                
                save_csv_data(data, get_path("expenses"))
                generate_account_history()
                
                st.success("¡Datos actualizados y guardados correctamente!")
                st.session_state.import_process = False
                st.rerun()
                
        with button_2: # Cancel button
            if st.button("Cancel", type="primary", use_container_width="True", disabled = False):
                st.session_state.import_process = False
                st.rerun()
        
    app_footer()


def show_export():
    # --- MAIN PAGE ---
    # Page state 
    change_page('EXPORT')
    
    st.write("Showing export tool..")
    
    
def show_settings():
    # --- MAIN PAGE ---
    # Page state 
    change_page('SETTINGS')

    st.write("Showing settings page...")
    
################################################### FUNCTIONS ###################################################
def change_page(new_page):
    """
    Description: Saves the page the user is currently on.
    Input: new_page (str) 
    Output: N/A
    """
    st.session_state.page = new_page

def balance_graph(date_ini, date_end, account, data):
    """
    Description: Shows an interactive bar chart with expenses, incomes and net balance.
    Input: date_ini (pandas datetime), date_end (pandas datetime), account (str), data (full expenses dataframe)
    Output: N/A
    """
    # --- Data filtering ---
    data = data[data['Fecha'].between(pd.to_datetime(date_ini), pd.to_datetime(date_end))]
    if account != "All":
        data = data[data['Cuenta'] == account]

    expenses = abs(data[data['Importe'] < 0]['Importe'].sum())
    incomes  = data[data['Importe'] > 0]['Importe'].sum()
    balance  = incomes - expenses

    print(f"{datetime.now()} DEBUG - expenses={expenses:.2f} / incomes={incomes:.2f} / balance={balance:.2f}")

    # --- Build DataFrame ---
    balance_color = '#29B094' if balance >= 0 else '#FF4B4B'

    df_bar = pd.DataFrame({
        'Categorie': ['Incomes','Expenses','Balance'],
        'Amount':   [incomes, expenses, abs(balance)],
        'Color':     ['#29B094', '#FF4B4B', balance_color],
        'Label':     [f"+{incomes:,.0f} €",f"-{expenses:,.0f} €", 
                      f"{'+'if balance>=0 else '-'}{abs(balance):,.0f} €"],
    })

    # --- Chart ---
    fig = go.Figure()

    for _, row in df_bar.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Categorie']],
            y=[row['Amount']],
            marker_color=row['Color'],
            marker_line_width=0,
            text=row['Label'],
            textposition='outside',         # Valor encima de la barra
            textfont=dict(size=16, color=row['Color'], family='Arial Black'),
            hovertemplate=(
                f"<b>{row['Categorie']}</b><br>"
                f"Amount: {row['Label']}<extra></extra>"
            ),
            width=0.5,                      # Barras más estilizadas
        ))

    fig.update_layout(
        showlegend=False,
        height=390,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title=None,
        yaxis_title=None,
        bargap=0.3,
        font=dict(size=15, family='Arial'),
        template='plotly_white',
        xaxis=dict(
            tickfont=dict(size=14, color='#555555'),
        ),
        yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)',       # Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # Línea base sutil
    fig.add_shape(
        type='line',
        x0=-0.5, x1=2.5, y0=0, y1=0,
        line=dict(color='#CCCCCC', width=1.5)
    )

    chart_config = {
        'staticPlot': False,        # Activamos hover (ya lo personalizamos)
        'displayModeBar': False,
    }

    st.plotly_chart(fig, use_container_width=True, config=chart_config)

def variation_graph(date_ini, date_end, account, data):
    """
    Description: Shows a variation table depending on the selected inputs.
    Input: date_ini (pandas datetime), date_end (pandas datetime), data (full expenses dataframe) 
    Output: N/A
    """
    # Data filtering
    data['date'] = pd.to_datetime(data['date'])
    data = data[data['date'].between(pd.to_datetime(date_ini), pd.to_datetime(date_end))] # date filter
    if account != "All":
        data = data[data['account'] == account] 
    
    print(f"{datetime.now()} DEBUG - the data before the error is: {data}")
    
    fig = px.line(
    data, 
    x='date', 
    y='amount', 
    color='account',       # Esto sustituye a tu bucle for
    markers=True,          # Añade puntos en los nodos
    title="Variation graph",
    template='plotly_white' # Estilo limpio
    )

    # 3. Mejoras visuales (sustituye a fig, ax = plt.subplots...)
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="€",
        legend_title="Cuentas",
        height=400,            # Altura similar a tu figsize=(5, 2)
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"  # Al pasar el ratón, ves todas las cuentas a la vez
    )

    config = {
        'staticPlot': True,        # El gráfico no reacciona a nada
        'displayModeBar': False    # No hay herramientas
        }

    # 4. Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True, config=config)

def pie_graph():
    """
    Description: Shows a pie graphic with the input data.
    Input: data (full expenses dataframe) 
    Output: N/A
    """   
    

def balance_kpis_and_table(date_ini, date_end, account, data_accounts, data_transactions):
    """
    Description: Shows 3 KPIs and a table with the variation of each account.
    Input: date_ini (pandas datetime), date_end (pandas datetime), account (str), data_accounts (dataframe with the history of accounts), data_transactions (full expenses dataframe)
    Output: N/A
    """
    date_ini_dt = pd.to_datetime(date_ini)
    date_end_dt = pd.to_datetime(date_end)
    data_accounts['date'] = pd.to_datetime(data_accounts['date'])

    # --- Filter by range and account ---
    df = data_accounts[data_accounts['date'].between(date_ini_dt, date_end_dt)]
    if account != "All":
        df = df[df['account'] == account]

    # --- KPI 1: Current total balance (last available date) ---
    last_date = df['date'].max()
    total_amount = df[df['date'] == last_date]['amount'].sum()

    # --- KPI 2: Daily average expense ---
    df_trans = data_transactions[data_transactions['Fecha'].between(date_ini_dt, date_end_dt)]
    if account != "All":
        df_trans = df_trans[df_trans['Cuenta'] == account]
    daily_expenses = df_trans[df_trans['Importe'] < 0].groupby('Fecha')['Importe'].sum()
    avg_daily_expense = abs(daily_expenses.mean()) if not daily_expenses.empty else 0

    # --- KPI 3: Top spending category ---
    df_expenses = df_trans[df_trans['Importe'] < 0]
    if not df_expenses.empty:
        top_category = df_expenses.groupby('Etiqueta 1')['Importe'].sum().idxmin()  # idxmin = most negative = most spent
        top_category_value = abs(df_expenses.groupby('Etiqueta 1')['Importe'].sum().min())
    else:
        top_category = "N/A"
        top_category_value = 0

    # --- Render KPIs in 3 columns ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Current total amount", value=f"{total_amount:,.0f} €")
    with col2:
        st.metric(label="📉 Avg. daily expense", value=f"{avg_daily_expense:,.0f} €/day")
    with col3:
        st.metric(label="🏷️ Top spending category", value=top_category, delta=f"-{top_category_value:,.0f} €", delta_color="inverse")

    st.divider()

    # --- Table by account ---
    first_date = df['date'].min()
    balance_start = df[df['date'] == first_date].groupby('account')['amount'].sum()
    balance_end   = df[df['date'] == last_date].groupby('account')['amount'].sum()
    variation     = (balance_end - balance_start).dropna()

    table = pd.DataFrame({
        'Account':       balance_start.index,
        'Start balance': balance_start.values,
        'End balance':   balance_end.reindex(balance_start.index).values,
        'Variation':     variation.reindex(balance_start.index).values,
        'Avg/day':       df.groupby('account')['amount'].mean().reindex(balance_start.index).values,
    })

    # Format columns
    for col in ['Start balance', 'End balance', 'Variation', 'Avg/day']:
        table[col] = table[col].map(lambda x: f"{x:+,.0f} €" if col == 'Variation' else f"{x:,.0f} €")

    st.dataframe(table, use_container_width=True, hide_index=True, height=38+(3*38)-10) # 38px header + 38px per row (max 4 rows without scroll)


def category_sunburst_graph(date_ini, date_end, account, data):
    """
    Description: Shows a sunburst chart with expenses breakdown by category (Etiqueta 1) and subcategory (Etiqueta 2).
    Input: date_ini (pandas datetime), date_end (pandas datetime), account (str), data (full expenses dataframe)
    Output: N/A
    """
    # --- Filter by range and account ---
    data = data[data['Fecha'].between(pd.to_datetime(date_ini), pd.to_datetime(date_end))]
    if account != "All":
        data = data[data['Cuenta'] == account]

    # --- Keep only expenses ---
    df_expenses = data[data['Importe'] < 0].copy()
    df_expenses['Importe'] = df_expenses['Importe'].abs()

    if df_expenses.empty:
        st.info("No expenses found for the selected period.")
        return

    # --- Group by Etiqueta 1 and Etiqueta 2 ---
    df_grouped = (
        df_expenses.groupby(['Etiqueta 1', 'Etiqueta 2'])['Importe']
        .sum()
        .reset_index()
    )

    # --- Sunburst chart ---
    fig = px.sunburst(
        df_grouped,
        path=['Etiqueta 1', 'Etiqueta 2'],
        values='Importe',
        color='Etiqueta 1',
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    fig.update_traces(
        textinfo='label+percent entry',
        hovertemplate='<b>%{label}</b><br>%{value:,.0f} €<br>%{percentEntry:.1%}<extra></extra>',
        marker=dict(line=dict(color="#AFAFAF", width=1)),
        insidetextorientation='radial',
    )

    fig.update_layout(
        height=460,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=13, family='Arial'),
        title="Expenses breakdown by category",
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def category_stats(date_ini, date_end, account, data):
    """
    Description: Shows top 3 spending categories as KPIs and a summary table by category.
    Input: date_ini (pandas datetime), date_end (pandas datetime), account (str), data (full expenses dataframe)
    Output: N/A
    """
    # --- Filter by range and account ---
    data = data[data['Fecha'].between(pd.to_datetime(date_ini), pd.to_datetime(date_end))]
    if account != "All":
        data = data[data['Cuenta'] == account]

    # --- Keep only expenses ---
    df_expenses = data[data['Importe'] < 0].copy()
    df_expenses['Importe'] = df_expenses['Importe'].abs()

    if df_expenses.empty:
        st.info("No expenses found for the selected period.")
        return

    total_global = df_expenses['Importe'].sum()

    # --- Group by Etiqueta 1 ---
    df_grouped = (
        df_expenses.groupby('Etiqueta 1')
        .agg(
            Total=('Importe', 'sum'),
            Transactions=('Importe', 'count'),
        )
        .reset_index()
        .sort_values('Total', ascending=False)
    )
    df_grouped['%'] = (df_grouped['Total'] / total_global * 100).round(1)

    # --- Top 3 KPIs ---
    top3 = df_grouped.head(3)
    cols = st.columns(3)
    medals = ['🥇', '🥈', '🥉']
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.metric(
                label=f"{medals[i]} {row['Etiqueta 1']}",
                value=f"{row['Total']:,.0f} €",
                delta=f"{row['%']}% of total",
                delta_color="off",
            )

    st.divider()

    # --- Summary table ---
    table = df_grouped.copy()
    table['Total']  = table['Total'].map(lambda x: f"{x:,.0f} €")
    table['%']      = table['%'].map(lambda x: f"{x}%")
    table.columns   = ['Category', 'Total', 'Transactions', '% of Total']
    table           = table[['Category', 'Total', '% of Total', 'Transactions']]

    st.dataframe(table, use_container_width=True, hide_index=True, height=38+(5*38)-14 # 38px header + 38px per row (max 4 rows without scroll)
)
    

def comments_kpi(data, filtered_data):
    """
    Description: Shows KPIs for the selected comment filter: first date, last date and total expenses.
    Input: data (full expenses dataframe), filtered_data (dataframe filtered by comment)
    Output: N/A
    """
    if filtered_data.empty:
        st.info("No records found for the selected comment.")
        return

    # --- Calculations ---
    first_date  = filtered_data['Fecha'].min().strftime('%d/%m/%Y')
    last_date   = filtered_data['Fecha'].max().strftime('%d/%m/%Y')
    total       = abs(filtered_data[filtered_data['Importe'] < 0]['Importe'].sum())
    n_trans     = len(filtered_data)

    # --- Render KPIs ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📅 First appearance", value=first_date)
    with col2:
        st.metric(label="📅 Last appearance", value=last_date)
    with col3:
        st.metric(label="💸 Total expenses", value=f"{total:,.0f} €", delta=f"{n_trans} transactions", delta_color="off")


def app_footer():
    """
    Description: Shows app version, date and author from config.py.
    Input: N/A
    Output: N/A
    """
    st.divider()
    st.caption(f"{config.APP_VERSION} - {config.APP_DATE}")
    st.caption(f"Compatible with: {', '.join(config.COMPATIBLE_BANKS)}")
    st.caption(f"Generated by: {config.APP_AUTHOR}")