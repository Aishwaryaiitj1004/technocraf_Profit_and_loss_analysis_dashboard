import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Technocraft Fashions — P&L Dashboard",
    page_icon="📊",
    layout="wide",
)

# ----------------------------
# LOAD EXCEL
# ----------------------------

excel_file = "pl_data.xlsx"

amravati_df = pd.read_excel(
    excel_file,
    sheet_name="Profit Loss-Amravati-25-26"
)

betul_df = pd.read_excel(
    excel_file,
    sheet_name="Profit Loss-Betul-25-26"
)

# ----------------------------
# HELPERS
# ----------------------------

def to_cr(series):
    return (series / 10000000).tolist()

def format_money(v):

    if v is None:
        return "—"

    sign = "-" if v < 0 else ""
    v = abs(v)

    if v >= 1:
        return f"{sign}₹{v:.2f} Cr"
    else:
        return f"{sign}₹{v*100:.0f} L"

# ----------------------------
# MONTHS
# ----------------------------

MONTHS = ["Apr '25","May '25","Jun '25","Jul '25","Aug '25",
          "Sep '25","Oct '25","Nov '25","Dec '25","Jan '26","Feb '26"]

# ----------------------------
# DATA FROM EXCEL
# ----------------------------

DATA = {

    "Amravati": {

        "Gross Sales": to_cr(amravati_df["Gross Sales"]),
        "Net Sales": to_cr(amravati_df["Net Sales"]),
        "Net P&L": to_cr(amravati_df["Net P&L"]),
        "EBITDA": to_cr(amravati_df["EBITDA"]),

        "EBITDA Margin %": amravati_df["EBITDA Margin %"].tolist(),

        "Throughput": to_cr(amravati_df["Throughput"]),
        "Fixed Costs": to_cr(amravati_df["Fixed Costs"]),
        "Total Expenses": to_cr(amravati_df["Total Expenses"]),
    },

    "Betul": {

        "Gross Sales": to_cr(betul_df["Gross Sales"]),
        "Net Sales": to_cr(betul_df["Net Sales"]),
        "Net P&L": to_cr(betul_df["Net P&L"]),
        "EBITDA": to_cr(betul_df["EBITDA"]),

        "EBITDA Margin %": betul_df["EBITDA Margin %"].tolist(),

        "Throughput": [None]*11,
        "Fixed Costs": [None]*11,
        "Total Expenses": [None]*11,
    }
}

# ----------------------------
# DASHBOARD
# ----------------------------

st.title("Technocraft Fashions – Profit & Loss Dashboard")

division = st.selectbox(
    "Division",
    ["Both","Amravati","Betul"]
)

metric = st.selectbox(
    "Metric",
    ["Net P&L","Gross Sales","EBITDA","EBITDA Margin %","Throughput"]
)

a = DATA["Amravati"]
b = DATA["Betul"]

# ----------------------------
# KPI
# ----------------------------

rev_a = sum(a["Gross Sales"])
pl_a = sum(a["Net P&L"])

rev_b = sum(b["Gross Sales"])
pl_b = sum(b["Net P&L"])

if division == "Amravati":

    total_rev = rev_a
    total_pl = pl_a

elif division == "Betul":

    total_rev = rev_b
    total_pl = pl_b

else:

    total_rev = rev_a + rev_b
    total_pl = pl_a + pl_b

c1, c2 = st.columns(2)

c1.metric("Period Revenue", format_money(total_rev))
c2.metric("Period Net P&L", format_money(total_pl))

# ----------------------------
# MAIN CHART
# ----------------------------

fig = go.Figure()

if division in ["Both","Amravati"]:

    fig.add_bar(
        name="Amravati",
        x=MONTHS,
        y=a[metric]
    )

if division in ["Both","Betul"]:

    fig.add_bar(
        name="Betul",
        x=MONTHS,
        y=b[metric]
    )

fig.update_layout(
    height=350
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# REVENUE VS EXPENSE
# ----------------------------

fig2 = go.Figure()

fig2.add_bar(
    name="Revenue",
    x=MONTHS,
    y=a["Gross Sales"]
)

fig2.add_bar(
    name="Expenses",
    x=MONTHS,
    y=a["Total Expenses"]
)

fig2.update_layout(
    title="Revenue vs Expenses (Amravati)",
    barmode="group"
)

st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# THROUGHOUT VS FIXED
# ----------------------------

fig3 = go.Figure()

fig3.add_bar(
    name="Throughput",
    x=MONTHS,
    y=a["Throughput"]
)

fig3.add_scatter(
    name="Fixed Expenses",
    x=MONTHS,
    y=a["Fixed Costs"]
)

fig3.update_layout(
    title="Throughput vs Fixed Expenses"
)

st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# TABLE
# ----------------------------

rows = []

for i, m in enumerate(MONTHS):

    rows.append({
        "Month": m,
        "Gross Sales": format_money(a["Gross Sales"][i]),
        "Net P&L": format_money(a["Net P&L"][i]),
        "EBITDA Margin": f"{a['EBITDA Margin %'][i]:.1f}%"
    })

df = pd.DataFrame(rows)

st.dataframe(df, use_container_width=True)
