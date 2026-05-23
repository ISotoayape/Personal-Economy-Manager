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
from functions import (save_csv_data, get_path, get_metrics, import_revolut, autofill,
                       get_account_name_list, import_caja_rural, generate_account_history,
                       import_trade_republic, import_csv_data)


_BANK_IMPORTERS = {
    "Revolut":        import_revolut,
    "Caja Rural":     import_caja_rural,
    "Trade Republic": import_trade_republic,
}


def _build_column_config(categories, subcategories, account_options):
    return {
        "key": st.column_config.NumberColumn("ID", width="small", min_value=0, required=True),
        "Concepto":   st.column_config.TextColumn("Concepto", width="medium", required=True),
        "Fecha":      st.column_config.DateColumn("Fecha", format="DD/MM/YYYY", required=True),
        "Cuenta":     st.column_config.SelectboxColumn("Cuenta", options=account_options, required=True),
        "Importe":    st.column_config.NumberColumn("Importe", format="%.2f €", required=True),
        "Etiqueta 1": st.column_config.SelectboxColumn("Etiqueta 1", options=categories, required=True),
        "Etiqueta 2": st.column_config.SelectboxColumn("Etiqueta 2", options=subcategories, required=True),
        "Comentario": st.column_config.TextColumn("Comentario", width="large"),
    }


def main_gui(importing_data, data, categories, subcategories, accounts, accounts_history_data, excluded_categories):
    # --- PAGE CONFIGURATION ---
    st.set_page_config(
        page_title=config.PG_TITLE,
        page_icon=config.PG_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if "page" not in st.session_state:
        st.session_state.page = "HOME"

    # --- SIDEBAR ---
    with st.sidebar:
        st.title(config.SB_TITLE)
        for label in ["HOME", "EXPENSES", "IMPORT", "EXPORT", "SETTINGS"]:
            st.button(label, on_click=change_page, args=[label],
                      type="secondary", use_container_width=True,
                      key=f"bttn_{label.lower()}")

    # --- ROUTER ---
    page = st.session_state.page
    if page == "HOME":
        show_home(data, categories, subcategories, accounts, accounts_history_data, excluded_categories)
    elif page == "EXPENSES":
        show_expenses(data, categories, subcategories)
    elif page == "IMPORT":
        show_import(data, categories, subcategories, accounts)
    elif page == "EXPORT":
        show_export()
    elif page == "SETTINGS":
        show_settings()


################################################### PAGES ###################################################
def show_home(data, categories, subcategories, accounts, accounts_history_data, excluded_categories):
    change_page('HOME')
    st.title("DASHBOARD")

    if not data.empty:
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
            accounts_list = ["All"] + data["Cuenta"].unique().tolist()
            selected_account = st.selectbox("Account", accounts_list, key="filter_account")

        st.markdown("---")

        col_1, col_2 = st.columns([0.33, 0.67])
        with col_1:
            balance_graph(selected_ini_date, selected_end_date, selected_account, data, excluded_categories)
        with col_2:
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            balance_kpis_and_table(selected_ini_date, selected_end_date, selected_account, accounts_history_data, data, excluded_categories)

        st.markdown("---")
        variation_graph(selected_ini_date, selected_end_date, selected_account, accounts_history_data)

        st.markdown("---")
        col_1, col_2 = st.columns([0.6, 0.4])
        with col_1:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            category_sunburst_graph(selected_ini_date, selected_end_date, selected_account, data, excluded_categories)
        with col_2:
            st.markdown("#### KPIs")
            category_stats(selected_ini_date, selected_end_date, selected_account, data, excluded_categories)

        st.markdown("---")
        col_1, col_2 = st.columns([0.6, 0.4])
        with col_1:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.subheader("Comment searcher")
        with col_2:
            options  = data['Comentario'].unique().tolist()
            selected = st.selectbox("Comment", options)

        if selected:
            filtered_data = data[data['Comentario'].str.contains(selected, case=False, na=False)]
            comments_kpi(data, filtered_data)
            st.dataframe(filtered_data[['Fecha', 'Concepto', 'Cuenta', 'Importe', 'Etiqueta 1', 'Etiqueta 2', 'Comentario']],
                         use_container_width=True,
                         height=38 + (len(filtered_data) * 38) - 10)

        app_footer()

    else:
        st.info("Please, import your first expenses ;)")


def show_expenses(data, categories, subcategories):
    change_page('EXPENSES')
    st.title("Edición de Gastos")

    if not data.empty:
        st.session_state.expenses_df = pd.DataFrame(data)
        column_config = _build_column_config(categories, subcategories, config.COMPATIBLE_BANKS)

        edited_df = st.data_editor(
            st.session_state.expenses_df,
            column_config=column_config,
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            height=725,
            key="dataeditor_expenses"
        )

        state     = st.session_state.dataeditor_expenses
        df_edited = bool(state["edited_rows"] or state["added_rows"] or state["deleted_rows"])

        if st.button("Guardar Cambios", type="primary", disabled=not df_edited):
            st.session_state.expenses_df = edited_df
            save_csv_data(edited_df, get_path("expenses"))
            st.success("¡Datos actualizados y guardados correctamente!")
            st.rerun()

        app_footer()

    else:
        st.info("Please, import your first expenses ;)")


def show_import(data, categories, subcategories, accounts):
    change_page('IMPORT')

    if 'import_process' not in st.session_state:
        st.session_state.import_process = False

    st.title("CSV IMPORT")

    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        importing_bank = st.selectbox("Cuenta", config.COMPATIBLE_BANKS, key="filter_bank")
    with col_2:
        importing_csv = st.file_uploader(
            "Selecciona tu extracto bancario",
            type=["csv", "xlsx", "pdf"],
            help="Arrastra aquí el fichero exportado de tu banca online")
    with col_3:
        ready_to_import = importing_bank is not None and importing_csv is not None and not st.session_state.import_process
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("IMPORT", use_container_width=True, type="primary", disabled=not ready_to_import):
            st.session_state.import_process = True
            importer = _BANK_IMPORTERS.get(importing_bank)
            if importer:
                importing_df = importer(importing_csv)
                importing_df = autofill(data, importing_df)
                st.session_state.importing_expenses = importing_df
            else:
                print(f"{datetime.now()} DEBUG - No importer configured for {importing_bank}")
            st.rerun()

    st.markdown("---")

    if st.session_state.import_process:
        column_config = _build_column_config(categories, subcategories, accounts['name'].tolist())

        importing_df = st.data_editor(
            st.session_state.importing_expenses,
            column_config=column_config,
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            height=500,
            key="dataeditor_importing_expenses"
        )

        button_1, button_2, _ = st.columns([0.15, 0.15, 0.7])
        with button_1:
            critical_columns = ['Key', 'Concepto', 'Fecha', 'Cuenta', 'Importe', 'Etiqueta 1', 'Etiqueta 2']
            not_ready = importing_df[critical_columns].isna().any().any()

            if st.button("Save", type="primary", use_container_width=True, disabled=not_ready):
                data = pd.concat([data, importing_df], axis=0, ignore_index=True)
                print(f"{datetime.now()} DEBUG - The new data frame is:\n{data}")
                save_csv_data(data, get_path("expenses"))
                generate_account_history()
                st.success("¡Datos actualizados y guardados correctamente!")
                st.session_state.import_process = False
                st.rerun()

        with button_2:
            if st.button("Cancel", type="primary", use_container_width=True):
                st.session_state.import_process = False
                st.rerun()

    app_footer()


def show_export():
    change_page('EXPORT')
    st.write("Showing export tool..")


def show_settings():
    change_page('SETTINGS')
    st.title("Configuración")

    accounts_data   = import_csv_data(get_path("accounts"))
    categories_data = import_csv_data(get_path("categories"))

    # ------------------------------------------------------------------ ACCOUNTS
    st.subheader("Cuentas Bancarias")

    if accounts_data is not None:
        edited_accounts = st.data_editor(
            accounts_data,
            column_config={
                "name":   st.column_config.TextColumn("Cuenta", required=True),
                "import": st.column_config.NumberColumn("Saldo Inicial", format="%.2f €", required=True),
            },
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            key="dataeditor_accounts",
        )

        state_acc  = st.session_state.dataeditor_accounts
        acc_edited = bool(state_acc["edited_rows"] or state_acc["added_rows"] or state_acc["deleted_rows"])

        if st.button("Guardar Cuentas", type="primary", disabled=not acc_edited, key="btn_save_accounts"):
            save_csv_data(edited_accounts, get_path("accounts"))
            st.success("¡Cuentas guardadas correctamente!")
            st.rerun()

    st.markdown("---")

    # --------------------------------------------------------------- CATEGORIES
    st.subheader("Etiquetas y Sub-etiquetas")
    st.caption("Marca 'Excluir de contabilidad' para que una etiqueta no aparezca en los gráficos de categorías (sí aparece en el gráfico temporal).")

    if categories_data is not None:
        if 'Excluir' not in categories_data.columns:
            categories_data.insert(1, 'Excluir', False)

        subcat_cols = [c for c in categories_data.columns if c.startswith('SubCat')]
        categories_data[subcat_cols] = categories_data[subcat_cols].fillna('').astype(str)

        cat_col_config = {
            "Cat":    st.column_config.TextColumn("Etiqueta", required=True, width="medium"),
            "Excluir": st.column_config.CheckboxColumn("Excluir de contabilidad", width="small"),
        }
        for i in range(1, 16):
            col = f"SubCat{i}"
            if col in categories_data.columns:
                cat_col_config[col] = st.column_config.TextColumn(f"Sub-etiqueta {i}", width="medium")

        edited_categories = st.data_editor(
            categories_data,
            column_config=cat_col_config,
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            key="dataeditor_categories",
        )

        state_cats  = st.session_state.dataeditor_categories
        cats_edited = bool(state_cats["edited_rows"] or state_cats["added_rows"] or state_cats["deleted_rows"])

        if st.button("Guardar Etiquetas", type="primary", disabled=not cats_edited, key="btn_save_categories"):
            save_csv_data(edited_categories, get_path("categories"))
            st.success("¡Etiquetas guardadas correctamente!")
            st.rerun()

    app_footer()


################################################### FUNCTIONS ###################################################
def change_page(new_page):
    st.session_state.page = new_page


def balance_graph(date_ini, date_end, account, data, excluded_categories=None):
    data = data[data['Fecha'].between(pd.to_datetime(date_ini), pd.to_datetime(date_end))]
    if account != "All":
        data = data[data['Cuenta'] == account]
    if excluded_categories:
        data = data[~data['Etiqueta 1'].isin(excluded_categories)]

    expenses = abs(data[data['Importe'] < 0]['Importe'].sum())
    incomes  = data[data['Importe'] > 0]['Importe'].sum()
    balance  = incomes - expenses

    print(f"{datetime.now()} DEBUG - expenses={expenses:.2f} / incomes={incomes:.2f} / balance={balance:.2f}")

    balance_color = '#29B094' if balance >= 0 else '#FF4B4B'
    df_bar = pd.DataFrame({
        'Categorie': ['Incomes', 'Expenses', 'Balance'],
        'Amount':    [incomes, expenses, abs(balance)],
        'Color':     ['#29B094', '#FF4B4B', balance_color],
        'Label':     [f"+{incomes:,.0f} €", f"-{expenses:,.0f} €",
                      f"{'+'if balance>=0 else '-'}{abs(balance):,.0f} €"],
    })

    fig = go.Figure()
    for _, row in df_bar.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Categorie']],
            y=[row['Amount']],
            marker_color=row['Color'],
            marker_line_width=0,
            text=row['Label'],
            textposition='outside',
            textfont=dict(size=16, color=row['Color'], family='Arial Black'),
            hovertemplate=f"<b>{row['Categorie']}</b><br>Amount: {row['Label']}<extra></extra>",
            width=0.5,
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
        xaxis=dict(tickfont=dict(size=14, color='#555555')),
        yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    fig.add_shape(type='line', x0=-0.5, x1=2.5, y0=0, y1=0,
                  line=dict(color='#CCCCCC', width=1.5))

    st.plotly_chart(fig, use_container_width=True,
                    config={'staticPlot': False, 'displayModeBar': False})


def variation_graph(date_ini, date_end, account, data):
    data = data.copy()
    data['date'] = pd.to_datetime(data['date'])
    data = data[data['date'].between(pd.to_datetime(date_ini), pd.to_datetime(date_end))]
    if account != "All":
        data = data[data['account'] == account]

    print(f"{datetime.now()} DEBUG - the data before the error is: {data}")

    fig = px.line(data, x='date', y='amount', color='account', markers=True,
                  title="Variation graph", template='plotly_white')
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="€",
        legend_title="Cuentas",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True,
                    config={'staticPlot': True, 'displayModeBar': False})


def balance_kpis_and_table(date_ini, date_end, account, data_accounts, data_transactions, excluded_categories=None):
    date_ini_dt = pd.to_datetime(date_ini)
    date_end_dt = pd.to_datetime(date_end)
    data_accounts = data_accounts.copy()
    data_accounts['date'] = pd.to_datetime(data_accounts['date'])

    df = data_accounts[data_accounts['date'].between(date_ini_dt, date_end_dt)]
    if account != "All":
        df = df[df['account'] == account]

    last_date    = df['date'].max()
    total_amount = df[df['date'] == last_date]['amount'].sum()

    df_trans = data_transactions[data_transactions['Fecha'].between(date_ini_dt, date_end_dt)]
    if account != "All":
        df_trans = df_trans[df_trans['Cuenta'] == account]
    if excluded_categories:
        df_trans = df_trans[~df_trans['Etiqueta 1'].isin(excluded_categories)]
    daily_expenses    = df_trans[df_trans['Importe'] < 0].groupby('Fecha')['Importe'].sum()
    avg_daily_expense = abs(daily_expenses.mean()) if not daily_expenses.empty else 0

    df_expenses = df_trans[df_trans['Importe'] < 0]
    if not df_expenses.empty:
        top_category       = df_expenses.groupby('Etiqueta 1')['Importe'].sum().idxmin()
        top_category_value = abs(df_expenses.groupby('Etiqueta 1')['Importe'].sum().min())
    else:
        top_category       = "N/A"
        top_category_value = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Current total amount", value=f"{total_amount:,.0f} €")
    with col2:
        st.metric(label="📉 Avg. daily expense", value=f"{avg_daily_expense:,.0f} €/day")
    with col3:
        st.metric(label="🏷️ Top spending category", value=top_category,
                  delta=f"-{top_category_value:,.0f} €", delta_color="inverse")

    st.divider()

    first_date    = df['date'].min()
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
    for col in ['Start balance', 'End balance', 'Variation', 'Avg/day']:
        table[col] = table[col].map(lambda x: f"{x:+,.0f} €" if col == 'Variation' else f"{x:,.0f} €")

    st.dataframe(table, use_container_width=True, hide_index=True, height=38 + (3 * 38) - 10)


def category_sunburst_graph(date_ini, date_end, account, data, excluded_categories=None):
    data = data[data['Fecha'].between(pd.to_datetime(date_ini), pd.to_datetime(date_end))]
    if account != "All":
        data = data[data['Cuenta'] == account]

    df_expenses = data[data['Importe'] < 0].copy()
    if excluded_categories:
        df_expenses = df_expenses[~df_expenses['Etiqueta 1'].isin(excluded_categories)]
    df_expenses['Importe'] = df_expenses['Importe'].abs()

    if df_expenses.empty:
        st.info("No expenses found for the selected period.")
        return

    df_grouped = (
        df_expenses.groupby(['Etiqueta 1', 'Etiqueta 2'])['Importe']
        .sum()
        .reset_index()
    )

    fig = px.sunburst(df_grouped, path=['Etiqueta 1', 'Etiqueta 2'], values='Importe',
                      color='Etiqueta 1', color_discrete_sequence=px.colors.qualitative.Set3)
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


def category_stats(date_ini, date_end, account, data, excluded_categories=None):
    data = data[data['Fecha'].between(pd.to_datetime(date_ini), pd.to_datetime(date_end))]
    if account != "All":
        data = data[data['Cuenta'] == account]

    df_expenses = data[data['Importe'] < 0].copy()
    if excluded_categories:
        df_expenses = df_expenses[~df_expenses['Etiqueta 1'].isin(excluded_categories)]
    df_expenses['Importe'] = df_expenses['Importe'].abs()

    if df_expenses.empty:
        st.info("No expenses found for the selected period.")
        return

    total_global = df_expenses['Importe'].sum()
    df_grouped = (
        df_expenses.groupby('Etiqueta 1')
        .agg(Total=('Importe', 'sum'), Transactions=('Importe', 'count'))
        .reset_index()
        .sort_values('Total', ascending=False)
    )
    df_grouped['%'] = (df_grouped['Total'] / total_global * 100).round(1)

    top3   = df_grouped.head(3)
    cols   = st.columns(3)
    medals = ['🥇', '🥈', '🥉']
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.metric(label=f"{medals[i]} {row['Etiqueta 1']}",
                      value=f"{row['Total']:,.0f} €",
                      delta=f"{row['%']}% of total",
                      delta_color="off")

    st.divider()

    table = df_grouped.copy()
    table['Total'] = table['Total'].map(lambda x: f"{x:,.0f} €")
    table['%']     = table['%'].map(lambda x: f"{x}%")
    table.columns  = ['Category', 'Total', 'Transactions', '% of Total']
    table          = table[['Category', 'Total', '% of Total', 'Transactions']]

    st.dataframe(table, use_container_width=True, hide_index=True, height=38 + (5 * 38) - 14)


def comments_kpi(data, filtered_data):
    if filtered_data.empty:
        st.info("No records found for the selected comment.")
        return

    first_date = filtered_data['Fecha'].min().strftime('%d/%m/%Y')
    last_date  = filtered_data['Fecha'].max().strftime('%d/%m/%Y')
    total      = abs(filtered_data[filtered_data['Importe'] < 0]['Importe'].sum())
    n_trans    = len(filtered_data)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📅 First appearance", value=first_date)
    with col2:
        st.metric(label="📅 Last appearance", value=last_date)
    with col3:
        st.metric(label="💸 Total expenses", value=f"{total:,.0f} €",
                  delta=f"{n_trans} transactions", delta_color="off")


def app_footer():
    st.divider()
    st.caption(f"{config.APP_VERSION} - {config.APP_DATE}")
    st.caption(f"Compatible with: {', '.join(config.COMPATIBLE_BANKS)}")
    st.caption(f"Generated by: {config.APP_AUTHOR}")
