import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Technocraft Fashions — P&L Dashboard",
    page_icon="📊",
    layout="wide",
)

# -----------------------------
# LOAD EXCEL
# -----------------------------

excel_file = "pl_data.xlsx"

amravati_df = pd.read_excel(excel_file, sheet_name=0, header=None)
betul_df = pd.read_excel(excel_file, sheet_name=1, header=None)

# -----------------------------
# HELPERS
# -----------------------------

def find_value(df, keyword):
    df = df.astype(str)

    match = df[df.apply(lambda row: row.str.contains(keyword, case=False).any(), axis=1)]

    if not match.empty:
        value = match.iloc[0,1]
        return float(value)

    return None


def to_cr(v):

    if v is None:
        return None

    return v / 10000000


def format_money(v):

    if v is None:
        return "—"

    sign = "-" if v < 0 else ""
    v = abs(v)

    if v >= 1:
        return f"{sign}₹{v:.2f} Cr"
    else:
        return f"{sign}₹{v*100:.0f} L"


# -----------------------------
# EXTRACT VALUES
# -----------------------------

gross_sales_a = to_cr(find_value(amravati_df, "GROSS SALES"))
throughput_a = to_cr(find_value(amravati_df, "THROUGHPUT"))
fixed_cost_a = to_cr(find_value(amravati_df, "FIXED"))
expenses_a = to_cr(find_value(amravati_df, "EXPENSE"))

gross_sales_b = to_cr(find_value(betul_df, "GROSS SALES"))

# -----------------------------
# DATA
# -----------------------------

DATA = {

    "Amravati": {

        "Gross Sales": gross_sales_a,
        "Throughput": throughput_a,
        "Fixed Costs": fixed_cost_a,
        "Total Expenses": expenses_a,

    },

    "Betul": {

        "Gross Sales": gross_sales_b,

    }
}

# -----------------------------
# DASHBOARD
# -----------------------------

st.title("Technocraft Fashions — Profit & Loss Dashboard")

division = st.selectbox("Division", ["Amravati","Betul"])

data = DATA[division]

# -----------------------------
# KPIs
# -----------------------------

col1, col2, col3 = st.columns(3)

col1.metric("Gross Sales", format_money(data.get("Gross Sales")))
col2.metric("Throughput", format_money(data.get("Throughput")))
col3.metric("Fixed Costs", format_money(data.get("Fixed Costs")))

st.markdown("---")

# -----------------------------
# CHART
# -----------------------------

labels = []
values = []

for k,v in data.items():
    if v is not None:
        labels.append(k)
        values.append(v)

fig = go.Figure()

fig.add_bar(
    x=labels,
    y=values
)

fig.update_layout(
    title=f"{division} Financial Overview",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TABLE
# -----------------------------

table_data = []

for k,v in data.items():

    table_data.append({
        "Metric": k,
        "Value": format_money(v)
    })

df = pd.DataFrame(table_data)

st.dataframe(df, use_container_width=True)

st.caption("Data Source: pl_data.xlsx")
