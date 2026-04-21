import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Technocraft Fashions — P&L Dashboard",
    page_icon="📊",
    layout="wide",
)

MONTHS = ["Apr '25","May '25","Jun '25","Jul '25","Aug '25",
          "Sep '25","Oct '25","Nov '25","Dec '25","Jan '26","Feb '26"]

DATA = {
    "Amravati": {
        "Gross Sales":[4.959,6.304,5.712,9.109,6.201,7.763,5.819,13.413,17.155,7.547,8.933],
        "Net Sales":[4.936,6.219,5.594,8.898,6.140,7.654,5.714,12.914,16.576,7.454,8.795],
        "Net P&L":[-1.373,-1.359,-2.517,-0.513,-2.670,-1.681,-2.460,0.735,0.355,-1.996,-2.113],
        "EBITDA":[-1.046,-1.014,-2.178,-0.123,-2.296,-1.298,-2.079,1.095,0.728,-1.623,-1.761],
        "EBITDA Margin %":[-21.07,-15.78,-38.45,-1.36,-36.33,-16.83,-35.16,8.15,4.24,-21.55,-19.57],
        "Throughput":[0.855,0.803,-0.061,2.053,-0.028,1.084,0.145,3.285,3.048,0.502,0.246],
        "Fixed Costs":[2.228,2.450,2.453,2.596,2.667,2.799,2.612,2.556,2.747,2.666,2.752],
        "Total Expenses":[6.335,8.072,8.178,9.584,9.016,9.424,8.380,12.705,16.853,9.697,11.505],
    },
    "Betul": {
        "Gross Sales":[0.15,0.10,0.28,0.37,0.32,0.32,0.11,0.21,0.32,0.33,0.20],
        "Net Sales":[0.15,0.10,0.28,0.37,0.32,0.32,0.10,0.21,0.32,0.33,0.20],
        "Net P&L":[-0.21,-0.26,-0.14,-0.07,-0.10,-0.10,-0.35,-0.27,-0.25,-0.23,-0.41],
        "EBITDA":[-0.15,-0.19,-0.07,-0.004,-0.02,-0.02,-0.27,-0.19,-0.16,-0.13,-0.32],
        "EBITDA Margin %":[-100.6,-193.8,-26.1,-1.1,-6.6,-6.3,-257.9,-88.7,-50.7,-40.6,-156.5],
        "Throughput":[None]*11,
        "Fixed Costs":[None]*11,
        "Total Expenses":[None]*11,
    }
}

# -------- FORMAT FUNCTION --------

def format_money(v):
    if v is None:
        return "—"

    sign = "-" if v < 0 else ""
    v = abs(v)

    if v >= 1:
        return f"{sign}₹{v:.2f} Cr"
    else:
        return f"{sign}₹{v*100:.0f} L"

# -------- HELPER --------

def s(arr,fr,to):
    if arr[0] is None:
        return [None]*(to-fr+1)
    return arr[fr:to+1]

# -------- HEADER --------

st.title("Technocraft Fashions – Profit & Loss Dashboard")

col1,col2,col3 = st.columns(3)

with col1:
    division = st.selectbox("Division",["Both","Amravati","Betul"])

with col2:
    metric = st.selectbox("Metric",
        ["Net P&L","Gross Sales","EBITDA","EBITDA Margin %","Throughput"])

with col3:
    month_range = st.select_slider(
        "Month Range",
        options=list(range(len(MONTHS))),
        value=(0,10),
        format_func=lambda x: MONTHS[x]
    )

fr,to = month_range
sel_months = MONTHS[fr:to+1]

a = DATA["Amravati"]
b = DATA["Betul"]

# -------- KPI --------

rev_a = sum(s(a["Gross Sales"],fr,to))
pl_a = sum(s(a["Net P&L"],fr,to))

rev_b = sum(s(b["Gross Sales"],fr,to))
pl_b = sum(s(b["Net P&L"],fr,to))

if division=="Amravati":
    total_rev,total_pl = rev_a,pl_a
elif division=="Betul":
    total_rev,total_pl = rev_b,pl_b
else:
    total_rev = rev_a+rev_b
    total_pl = pl_a+pl_b

c1,c2 = st.columns(2)

c1.metric("Period Revenue",format_money(total_rev))
c2.metric("Period Net P&L",format_money(total_pl))

# -------- MAIN CHART --------

fig = go.Figure()
is_margin = metric=="EBITDA Margin %"

if division in ["Both","Amravati"]:
    vals = s(a[metric],fr,to)
    fig.add_bar(name="Amravati",x=sel_months,y=vals)

if division in ["Both","Betul"]:
    vals = s(b[metric],fr,to)
    fig.add_bar(name="Betul",x=sel_months,y=vals)

fig.update_layout(
    height=350,
    yaxis_ticksuffix="%" if is_margin else ""
)

st.plotly_chart(fig,use_container_width=True)

# -------- REVENUE VS EXPENSE --------

gross = s(a["Gross Sales"],fr,to)
exp = s(a["Total Expenses"],fr,to)

fig2 = go.Figure()

fig2.add_bar(name="Revenue",x=sel_months,y=gross)
fig2.add_bar(name="Expenses",x=sel_months,y=exp)

fig2.update_layout(
    title="Revenue vs Expenses (Amravati)",
    barmode="group"
)

st.plotly_chart(fig2,use_container_width=True)

# -------- THROUGHOUT VS FIXED --------

through = s(a["Throughput"],fr,to)
fixed = s(a["Fixed Costs"],fr,to)

fig3 = go.Figure()

fig3.add_bar(name="Throughput",x=sel_months,y=through)
fig3.add_scatter(name="Fixed Expenses",x=sel_months,y=fixed)

fig3.update_layout(
    title="Throughput vs Fixed Expenses"
)

st.plotly_chart(fig3,use_container_width=True)

# -------- TABLE --------

rows=[]

for i,m in enumerate(sel_months):

    rev = s(a["Gross Sales"],fr,to)[i]
    pl = s(a["Net P&L"],fr,to)[i]
    em = s(a["EBITDA Margin %"],fr,to)[i]

    rows.append({
        "Month":m,
        "Gross Sales":format_money(rev),
        "Net P&L":format_money(pl),
        "EBITDA Margin":f"{em:.1f}%"
    })

df = pd.DataFrame(rows)

st.dataframe(df,use_container_width=True)
