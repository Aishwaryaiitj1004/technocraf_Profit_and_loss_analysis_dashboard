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

# -----------------------------
# MONTHS
# -----------------------------

months = [
"Apr 25","May 25","Jun 25","Jul 25","Aug 25",
"Sep 25","Oct 25","Nov 25","Dec 25","Jan 26","Feb 26"
]

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def get_row_values(df, label):

    row = df[df.iloc[:,0].astype(str).str.contains(label, case=False, na=False)]

    if row.empty:
        return []

    values = row.iloc[0,1:12].tolist()

    cleaned = []

    for v in values:
        try:
            cleaned.append(float(str(v).replace(",", "")) / 10000000)
        except:
            cleaned.append(None)

    return cleaned


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
# FETCH DATA
# -----------------------------

gross_sales = get_row_values(amravati_df, "GROSS SALES")
net_sales = get_row_values(amravati_df, "NET SALES")
throughput = get_row_values(amravati_df, "THROUGHPUT")
fixed_expenses = get_row_values(amravati_df, "TOTAL FIXED EXPENSES")
ebitda = get_row_values(amravati_df, "EBIDTA")

# -----------------------------
# DASHBOARD TITLE
# -----------------------------

st.title("Technocraft Fashions Limited")
st.subheader("Profit & Loss Dashboard (Apr 2025 – Feb 2026)")

st.markdown("---")

# -----------------------------
# KPI CARDS
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("Gross Sales (Feb)", format_money(gross_sales[-1]))
col2.metric("Net Sales (Feb)", format_money(net_sales[-1]))
col3.metric("Throughput (Feb)", format_money(throughput[-1]))
col4.metric("Fixed Expenses (Feb)", format_money(fixed_expenses[-1]))

st.markdown("---")

# -----------------------------
# SALES TREND
# -----------------------------

fig_sales = go.Figure()

fig_sales.add_trace(go.Scatter(
    x=months,
    y=gross_sales,
    mode="lines+markers",
    name="Gross Sales"
))

fig_sales.add_trace(go.Scatter(
    x=months,
    y=net_sales,
    mode="lines+markers",
    name="Net Sales"
))

fig_sales.update_layout(
    title="Monthly Sales Trend",
    height=400
)

st.plotly_chart(fig_sales, use_container_width=True)

# -----------------------------
# THROUGHPUT VS FIXED EXPENSES
# -----------------------------

fig_tp = go.Figure()

fig_tp.add_bar(
    x=months,
    y=throughput,
    name="Throughput"
)

fig_tp.add_trace(go.Scatter(
    x=months,
    y=fixed_expenses,
    mode="lines+markers",
    name="Fixed Expenses"
))

fig_tp.update_layout(
    title="Throughput vs Fixed Expenses",
    height=400
)

st.plotly_chart(fig_tp, use_container_width=True)

# -----------------------------
# EBITDA TREND
# -----------------------------

fig_ebitda = go.Figure()

fig_ebitda.add_bar(
    x=months,
    y=ebitda,
    name="EBITDA"
)

fig_ebitda.update_layout(
    title="EBITDA Trend",
    height=400
)

st.plotly_chart(fig_ebitda, use_container_width=True)

# -----------------------------
# TABLE
# -----------------------------

df_table = pd.DataFrame({
    "Month": months,
    "Gross Sales": gross_sales,
    "Net Sales": net_sales,
    "Throughput": throughput,
    "Fixed Expenses": fixed_expenses,
    "EBITDA": ebitda
})

st.markdown("### Monthly Breakdown")

st.dataframe(df_table, use_container_width=True)
