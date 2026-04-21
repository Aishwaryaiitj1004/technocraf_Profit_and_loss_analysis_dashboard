import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(
    page_title="Technocraft Fashions – Operational Insights — Profit & Loss Dashboard Apr 2025 – Feb 2026",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
.metric-card { background: #f8f9fa; border-radius: 10px; padding: 1rem 1.2rem; }
h1 { font-size: 1.4rem !important; }
</style>
""", unsafe_allow_html=True)

MONTHS = ["Apr '25", "May '25", "Jun '25", "Jul '25", "Aug '25",
          "Sep '25", "Oct '25", "Nov '25", "Dec '25", "Jan '26", "Feb '26"]

DATA = {
    "Amravati": {
        "Gross Sales":    [4.96, 6.30, 5.71, 9.11, 6.20, 7.76, 5.82, 13.41, 17.16, 7.55, 8.93],
        "Net Sales":      [4.94, 6.22, 5.59, 8.90, 6.14, 7.65, 5.71, 12.91, 16.58, 7.45, 8.80],
        "Net P&L":        [-1.37, -1.36, -2.52, -0.51, -2.67, -1.68, -2.46, 0.73, 0.35, -2.00, -2.11],
        "EBITDA":         [-1.05, -1.01, -2.18, -0.12, -2.30, -1.30, -2.08, 1.09, 0.73, -1.62, -1.76],
        "EBITDA Margin %":[-21.07,-15.78,-38.45,-1.36,-36.33,-16.83,-35.16,8.15,4.24,-21.55,-19.57],
        "Throughput":     [0.85, 0.80, -0.06, 2.05, -0.03, 1.08, 0.15, 3.29, 3.05, 0.50, 0.25],
        "Fixed Costs":    [2.23, 2.45, 2.45, 2.60, 2.67, 2.80, 2.61, 2.56, 2.75, 2.67, 2.75],
        "Total Expenses": [6.33, 8.07, 8.18, 9.58, 9.02, 9.42, 8.38, 12.71, 16.85, 9.70, 11.50],
    },
    "Betul": {
        "Gross Sales":    [0.15, 0.10, 0.28, 0.37, 0.32, 0.32, 0.11, 0.21, 0.32, 0.33, 0.20],
        "Net Sales":      [0.15, 0.10, 0.28, 0.37, 0.32, 0.32, 0.10, 0.21, 0.32, 0.33, 0.20],
        "Net P&L":        [-0.21, -0.26, -0.14, -0.07, -0.10, -0.10, -0.35, -0.27, -0.25, -0.23, -0.41],
        "EBITDA":         [-0.15, -0.19, -0.07, -0.004, -0.02, -0.02, -0.27, -0.19, -0.16, -0.13, -0.32],
        "EBITDA Margin %":[-100.6,-193.8,-26.1,-1.1,-6.6,-6.3,-257.9,-88.7,-50.7,-40.6,-156.5],
        "Throughput":     [None]*11,
        "Fixed Costs":    [None]*11,
        "Total Expenses": [None]*11,
    }
}

st.markdown("## 📊 Technocraft Fashions — P&L Dashboard")
st.caption("Amravati & Betul Divisions · April 2025 – February 2026")

st.markdown("---")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.5, 2, 2])
with col_ctrl1:
    division = st.selectbox("Division", ["Both", "Amravati", "Betul"], index=0)
with col_ctrl2:
    metric = st.selectbox("Metric", ["Net P&L", "Gross Sales", "EBITDA", "EBITDA Margin %", "Throughput"], index=0)
with col_ctrl3:
    month_range = st.select_slider(
        "Month range",
        options=list(range(11)),
        value=(0, 10),
        format_func=lambda x: MONTHS[x]
    )

fr, to = month_range
sel_months = MONTHS[fr:to+1]

def s(arr):
    if arr[0] is None:
        return [None]*(to-fr+1)
    return arr[fr:to+1]

def fmt_cr(v):
    if v is None: return "—"
    sign = "-" if v < 0 else ""
    return f"{sign}₹{abs(v):.2f} Cr"

def color_val(v):
    if v is None: return "gray"
    return "green" if v >= 0 else "red"

st.markdown("---")

a = DATA["Amravati"]
b = DATA["Betul"]

rev_a = sum(s(a["Gross Sales"]))
pl_a  = sum(s(a["Net P&L"]))
rev_b = sum(s(b["Gross Sales"]))
pl_b  = sum(s(b["Net P&L"]))

if division == "Amravati":
    total_rev, total_pl = rev_a, pl_a
elif division == "Betul":
    total_rev, total_pl = rev_b, pl_b
else:
    total_rev = rev_a + rev_b
    total_pl  = pl_a + pl_b

pl_a_vals  = s(a["Net P&L"])
best_idx   = pl_a_vals.index(max(pl_a_vals))
best_month = sel_months[best_idx]
best_val   = pl_a_vals[best_idx]

margins = s(a["EBITDA Margin %"])
avg_margin = sum(margins) / len(margins)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Period revenue", fmt_cr(total_rev))
c2.metric("Period net P&L", fmt_cr(total_pl), delta=None)
c3.metric("Best month (Amravati)", f"{best_month}: {fmt_cr(best_val)}")
c4.metric("Avg EBITDA margin (A)", f"{avg_margin:.1f}%")

st.markdown("---")

def bar_colors(vals):
    return ["#2ecc71" if (v or 0) >= 0 else "#e74c3c" for v in vals]

fig_main = go.Figure()
is_margin = metric == "EBITDA Margin %"
y_suffix = "%" if is_margin else " Cr"

if division in ["Both", "Amravati"]:
    vals = s(a[metric])
    if vals[0] is not None:
        fig_main.add_trace(go.Bar(
            name="Amravati", x=sel_months, y=vals,
            marker_color=bar_colors(vals),
            marker_line_width=0,
        ))

if division in ["Both", "Betul"]:
    vals_b = s(b[metric])
    if vals_b[0] is not None:
        fig_main.add_trace(go.Bar(
            name="Betul", x=sel_months, y=vals_b,
            marker_color="#9b59b6",
            marker_line_width=0,
            opacity=0.75,
        ))

fig_main.add_hline(y=0, line_width=1, line_color="gray", opacity=0.5)
fig_main.update_layout(
    title=f"{metric} — {division}",
    barmode="group",
    height=320,
    margin=dict(l=10, r=10, t=40, b=10),
    yaxis_ticksuffix=y_suffix,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    font=dict(size=12),
)
st.plotly_chart(fig_main, use_container_width=True)

col_left, col_right = st.columns(2)

with col_left:
    gross = s(a["Gross Sales"])
    exps  = s(a["Total Expenses"])
    fig_re = go.Figure()
    fig_re.add_trace(go.Bar(name="Revenue", x=sel_months, y=gross, marker_color="#3498db", opacity=0.8, marker_line_width=0))
    fig_re.add_trace(go.Bar(name="Expenses", x=sel_months, y=exps, marker_color="#e74c3c", opacity=0.8, marker_line_width=0))
    fig_re.update_layout(
        title="Revenue vs Expenses (Amravati)",
        barmode="group", height=280,
        margin=dict(l=10,r=10,t=40,b=10),
        yaxis_ticksuffix=" Cr",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(size=11),
    )
    st.plotly_chart(fig_re, use_container_width=True)

with col_right:
    through = s(a["Throughput"])
    fixed   = s(a["Fixed Costs"])
    t_colors = ["#27ae60" if (v or 0) >= 0 else "#e74c3c" for v in through]
    fig_t = go.Figure()
    fig_t.add_trace(go.Bar(name="Throughput", x=sel_months, y=through, marker_color=t_colors, opacity=0.8, marker_line_width=0))
    fig_t.add_trace(go.Scatter(name="Fixed costs", x=sel_months, y=fixed, mode="lines+markers",
                               line=dict(color="#e74c3c", width=2, dash="dot"),
                               marker=dict(size=6, color="#e74c3c")))
    fig_t.add_hline(y=0, line_width=1, line_color="gray", opacity=0.4)
    fig_t.update_layout(
        title="Throughput vs Fixed Costs (Amravati)",
        height=280,
        margin=dict(l=10,r=10,t=40,b=10),
        yaxis_ticksuffix=" Cr",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(size=11),
    )
    st.plotly_chart(fig_t, use_container_width=True)

st.markdown("---")
st.subheader("Month-by-month breakdown")

metric_vals = s(a[metric]) if division != "Betul" else s(b[metric])
table_data = []
for i, m in enumerate(sel_months):
    v = metric_vals[i]
    rev_v = s(a["Gross Sales"])[i] if division != "Betul" else s(b["Gross Sales"])[i]
    pl_v  = s(a["Net P&L"])[i]    if division != "Betul" else s(b["Net P&L"])[i]
    em_v  = s(a["EBITDA Margin %"])[i] if division != "Betul" else s(b["EBITDA Margin %"])[i]
    table_data.append({
        "Month": m,
        "Gross Sales (₹Cr)": f"{rev_v:.2f}" if rev_v else "—",
        "Net P&L (₹Cr)": f"{pl_v:.2f}" if pl_v else "—",
        "EBITDA Margin": f"{em_v:.1f}%" if em_v else "—",
        f"{metric} (selected)": f"{v:.2f}{'%' if is_margin else ' Cr'}" if v else "—",
    })

df = pd.DataFrame(table_data)

def color_pl(val):
    try:
        num = float(str(val).replace("₹","").replace("Cr","").replace("%","").strip())
        if num >= 0: return "color: #27ae60; font-weight: 500"
        else: return "color: #e74c3c; font-weight: 500"
    except:
        return ""

try:
    styled = df.style.map(color_pl, subset=["Net P&L (₹Cr)", "EBITDA Margin", f"{metric} (selected)"])
except AttributeError:
    styled = df.style.applymap(color_pl, subset=["Net P&L (₹Cr)", "EBITDA Margin", f"{metric} (selected)"])
st.dataframe(styled, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Data source: Profit & Loss — Fashions Amravati and Betul, Feb 2026 · Built with Streamlit + Plotly")
