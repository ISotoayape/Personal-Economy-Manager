# PEconomy - Personal Economy Manager

Aplicacion web de gestion de finanzas personales construida con Python y Streamlit. Centraliza y analiza gastos e ingresos de multiples cuentas bancarias.

---

## Stack tecnologico

- **Python** con **Streamlit** como framework web
- **Pandas** para manipulacion de datos
- **Plotly / Matplotlib** para graficos
- **pdfplumber** para lectura de PDFs bancarios

---

## Estructura del proyecto

```text
bin/
  main.py       → punto de entrada, arranca la app
  config.py     → constantes (rutas, version, configuracion GUI)
  functions.py  → logica de negocio (lectura CSV, importacion, calculos)
  gui.py        → interfaz Streamlit (paginas y componentes)
data/
  expenses.csv           → gastos registrados
  importing_expenses.csv → staging de gastos a importar
  categories.csv         → categorias, subcategorias y flag de exclusion
  bankaccounts.csv       → cuentas bancarias y saldo inicial
  account_history.csv    → historial de saldo por cuenta (generado automaticamente)
$$_importing csvs/       → archivos fuente de los bancos (xlsx, csv, pdf)
```

---

## Paginas de la aplicacion

| Pagina       | Funcion                                                |
| ------------ | ------------------------------------------------------ |
| **HOME**     | Dashboard con metricas, KPIs y graficos                |
| **EXPENSES** | Listado editable de todos los gastos                   |
| **IMPORT**   | Importar movimientos desde el banco                    |
| **EXPORT**   | Exportar datos (pendiente de implementar)              |
| **SETTINGS** | Gestion de cuentas bancarias y etiquetas               |

---

## Bancos compatibles (importacion)

| Banco            | Formato | Notas                                    |
| ---------------- | ------- | ---------------------------------------- |
| Revolut          | CSV     |                                          |
| Caja Rural       | Excel   | Salta las 3 primeras filas de cabecera   |
| Trade Republic   | PDF     | Parseo con regex linea a linea           |
| Imagin           | —       | Configurado, sin parser implementado     |

---

## Flujo principal

1. Al arrancar, `generate_account_history()` recalcula el historial de saldos desde cero
2. Se leen todos los CSVs: gastos, categorias, cuentas e historial
3. La GUI Streamlit se sirve con las paginas navegables por la barra lateral
4. En **IMPORT** el usuario sube un extracto bancario, se normaliza al formato interno, se etiquetan los movimientos y se anaden a `expenses.csv`
5. La funcion `autofill()` aplica automaticamente las ultimas etiquetas/comentarios conocidos para cada concepto

---

## Datos de un gasto

Cada registro en `expenses.csv` tiene los siguientes campos:

| Campo      | Tipo     | Descripcion                        |
| ---------- | -------- | ---------------------------------- |
| Key        | int      | Identificador unico                |
| Fecha      | date     | Fecha de la operacion              |
| Concepto   | str      | Descripcion del movimiento         |
| Cuenta     | str      | Cuenta bancaria                    |
| Importe    | float    | Cantidad (negativo = gasto)        |
| Etiqueta 1 | str      | Categoria principal                |
| Etiqueta 2 | str      | Subcategoria                       |
| Comentario | str      | Nota libre del usuario             |

---

## Configuracion (SETTINGS)

### Cuentas bancarias (`bankaccounts.csv`)

Tabla editable con el nombre de cada cuenta y su saldo inicial. Los cambios se guardan directamente en el CSV.

### Etiquetas (`categories.csv`)

Tabla editable con las categorias principales, sus subcategorias (hasta 15) y un flag de exclusion por categoria:

- **Excluir de contabilidad**: si esta marcado, los gastos de esa categoria no se contabilizan en el balance (barra de ingresos/gastos/balance), los KPIs ni los graficos de categorias. El grafico temporal de saldo sigue mostrando todos los movimientos reales.

Caso de uso tipico: marcar `9-Traspasos Propios` como excluido para que los movimientos entre cuentas propias no distorsionen las metricas de gasto.

---

## Ejecucion

```bash
cd bin
streamlit run main.py
```
