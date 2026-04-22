import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Technocraft Fashions — P&L Dashboard",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.block-container { padding-top: 1.2rem; padding-bottom: 1rem; padding-left: 2rem; padding-right: 2rem; }

/* KPI Cards */
.kpi-box {
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.kpi-box.red  { border-left-color: #ef4444; }
.kpi-box.green{ border-left-color: #22c55e; }
.kpi-box.amber{ border-left-color: #f59e0b; }
.kpi-box.blue { border-left-color: #3b82f6; }
.kpi-box.purple{ border-left-color: #8b5cf6; }

.kpi-label { font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
             letter-spacing: 0.08em; color: #6b7280; margin-bottom: 4px; }
.kpi-value { font-size: 1.55rem; font-weight: 700; line-height: 1.1; color: #111827; }
.kpi-value.red   { color: #ef4444; }
.kpi-value.green { color: #16a34a; }
.kpi-value.amber { color: #d97706; }
.kpi-sub   { font-size: 0.68rem; color: #9ca3af; margin-top: 4px; }

/* Section header */
.section-hdr {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: #6b7280; margin: 0.8rem 0 0.4rem;
    padding-bottom: 6px; border-bottom: 1px solid #e5e7eb;
}

/* Tabs overrides */
div[data-testid="stHorizontalBlock"] { gap: 0.6rem; }

/* Sidebar */
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
MONTHS = ["Apr '25", "May '25", "Jun '25", "Jul '25", "Aug '25",
          "Sep '25", "Oct '25", "Nov '25", "Dec '25", "Jan '26", "Feb '26"]

DATA = {
    "Amravati": {
        "Gross Sales":     [4.959, 6.304, 5.712, 9.109, 6.201, 7.763, 5.819, 13.413, 17.155, 7.547, 8.933],
        "Net Sales":       [4.936, 6.219, 5.594, 8.898, 6.140, 7.654, 5.714, 12.914, 16.576, 7.454, 8.795],
        "Net P&L":         [-1.373,-1.359,-2.517,-0.513,-2.670,-1.681,-2.460, 0.735, 0.355,-1.996,-2.113],
        "EBITDA":          [-1.046,-1.014,-2.178,-0.123,-2.296,-1.298,-2.079, 1.095, 0.728,-1.623,-1.761],
        "EBITDA Margin %": [-21.07,-15.78,-38.45,-1.36,-36.33,-16.83,-35.16,  8.15,  4.24,-21.55,-19.57],
        "Throughput":      [ 0.855, 0.803,-0.061, 2.053,-0.028, 1.084, 0.145, 3.285, 3.048, 0.502, 0.246],
        "Fixed Costs":     [ 2.228, 2.450, 2.453, 2.596, 2.667, 2.799, 2.612, 2.556, 2.747, 2.666, 2.752],
        "Total Expenses":  [ 6.335, 8.072, 8.178, 9.584, 9.016, 9.424, 8.380,12.705,16.853, 9.697,11.505],
    },
    "Betul": {
        "Gross Sales":     [0.150, 0.100, 0.280, 0.370, 0.320, 0.320, 0.110, 0.210, 0.320, 0.330, 0.200],
        "Net Sales":       [0.150, 0.100, 0.280, 0.370, 0.320, 0.320, 0.100, 0.210, 0.320, 0.330, 0.200],
        "Net P&L":         [-0.210,-0.260,-0.140,-0.070,-0.100,-0.100,-0.350,-0.270,-0.250,-0.230,-0.410],
        "EBITDA":          [-0.150,-0.190,-0.070,-0.004,-0.020,-0.020,-0.270,-0.190,-0.160,-0.130,-0.320],
        "EBITDA Margin %": [-100.6,-193.8,-26.1, -1.1,  -6.6,  -6.3,-257.9,-88.7, -50.7,-40.6,-156.5],
        "Throughput":      [None]*11,
        "Fixed Costs":     [None]*11,
        "Total Expenses":  [None]*11,
    }
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def slice_data(arr, fr, to):
    if arr[0] is None:
        return [None] * (to - fr + 1)
    return arr[fr:to+1]

def fmt_cr(v, parens=False):
    if v is None: return "—"
    if parens and v < 0:
        return f"(₹{abs(v):.2f} Cr)"
    sign = "-" if v < 0 else ""
    return f"{sign}₹{abs(v):.2f} Cr"

def bar_colors(vals, pos_col="#3b82f6", neg_col="#ef4444"):
    return [pos_col if (v or 0) >= 0 else neg_col for v in vals]

def chart_layout(title, height=300, y_suffix=" Cr"):
    return dict(
        title=dict(text=title, font=dict(size=13, color="#374151"), x=0),
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis_ticksuffix=y_suffix,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        font=dict(size=11, family="Inter"),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#f3f4f6", gridwidth=1),
    )

def kpi_html(label, value, color="blue", sub=""):
    return f"""
    <div class="kpi-box {color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {color if color in ('red','green','amber') else ''}">{value}</div>
        {'<div class="kpi-sub">' + sub + '</div>' if sub else ''}
    </div>"""

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛️ Filters")
    st.markdown("---")
    division = st.selectbox("Division", ["Both", "Amravati", "Betul"], index=0)
    metric   = st.selectbox("Primary Metric", ["Net P&L", "Gross Sales", "EBITDA", "EBITDA Margin %", "Throughput"], index=0)
    month_range = st.select_slider(
        "Month Range",
        options=list(range(11)),
        value=(0, 10),
        format_func=lambda x: MONTHS[x]
    )
    st.markdown("---")
    show_cumulative = st.checkbox("Show cumulative trend", value=True)
    st.markdown("---")
    st.caption("Technocraft Fashions Ltd.\nFY 2025–26 | Apr–Feb")

fr, to = month_range
sel_months = MONTHS[fr:to+1]
a = DATA["Amravati"]
b = DATA["Betul"]
sa = lambda k: slice_data(a[k], fr, to)
sb = lambda k: slice_data(b[k], fr, to)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:0.2rem;'>
  <div>
    <div style='font-size:1.35rem; font-weight:700; color:#111827;'>📊 Technocraft Fashions — P&L Dashboard</div>
    <div style='font-size:0.78rem; color:#6b7280; margin-top:2px;'>Amravati &amp; Betul Divisions &nbsp;|&nbsp; Apr 2025 – Feb 2026</div>
  </div>
  <div style='background:#f3f4f6; padding:6px 14px; border-radius:8px; font-size:0.72rem; font-weight:600; color:#374151;'>
    FY 2025–26
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
rev_a  = sum(sa("Gross Sales"))
pl_a   = sum(sa("Net P&L"))
rev_b  = sum(sb("Gross Sales"))
pl_b   = sum(sb("Net P&L"))
exp_a  = sum(sa("Total Expenses"))

total_rev = rev_a + rev_b if division == "Both" else (rev_a if division == "Amravati" else rev_b)
total_pl  = pl_a  + pl_b  if division == "Both" else (pl_a  if division == "Amravati" else pl_b)

pl_a_vals   = sa("Net P&L")
best_idx    = pl_a_vals.index(max(pl_a_vals))
best_month  = sel_months[best_idx]
best_val    = pl_a_vals[best_idx]

margins     = sa("EBITDA Margin %")
avg_margin  = sum(margins) / len(margins)

pl_color    = "green" if total_pl >= 0 else "red"
margin_color= "green" if avg_margin >= 0 else "amber"
best_color  = "green" if best_val >= 0 else "amber"

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(kpi_html("Period Revenue", fmt_cr(total_rev), "blue",
                         f"{division} | {sel_months[0]}–{sel_months[-1]}"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_html("Period Net P&L", fmt_cr(total_pl, parens=True), pl_color,
                         "Profit ✅" if total_pl >= 0 else "Loss ⚠️"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_html("Total Expenses (A)", fmt_cr(exp_a), "red",
                         "Amravati only"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_html("Best Month (A)", f"{best_month}", best_color,
                         fmt_cr(best_val)), unsafe_allow_html=True)
with c5:
    st.markdown(kpi_html("Avg EBITDA Margin (A)", f"{avg_margin:.1f}%", margin_color,
                         "Amravati avg"), unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Primary Metric", "💰 Revenue & Expenses", "📊 Throughput & Fixed Costs", "📋 Detailed Table"])

# ── TAB 1: Primary metric bar chart + cumulative line ──
with tab1:
    is_margin = metric == "EBITDA Margin %"
    y_sfx = "%" if is_margin else " Cr"

    col_main, col_cum = st.columns([3, 2]) if show_cumulative else (st.columns([1])[0], None)

    with col_main:
        fig_main = go.Figure()
        if division in ["Both", "Amravati"]:
            vals = sa(metric)
            if vals[0] is not None:
                fig_main.add_trace(go.Bar(
                    name="Amravati", x=sel_months, y=vals,
                    marker_color=bar_colors(vals, "#3b82f6", "#ef4444"),
                    marker_line_width=0, text=[f"{v:.1f}" for v in vals],
                    textposition="outside", textfont=dict(size=9),
                ))
        if division in ["Both", "Betul"]:
            vals_b = sb(metric)
            if vals_b[0] is not None:
                fig_main.add_trace(go.Bar(
                    name="Betul", x=sel_months, y=vals_b,
                    marker_color="#8b5cf6", marker_line_width=0, opacity=0.8,
                ))
        fig_main.add_hline(y=0, line_width=1, line_color="#9ca3af", opacity=0.6)
        fig_main.update_layout(**chart_layout(f"{metric} — {division}", height=330, y_suffix=y_sfx))
        st.plotly_chart(fig_main, use_container_width=True)

    if show_cumulative and col_cum:
        with col_cum:
            # Cumulative P&L
            cum_pl_a = []
            running = 0
            for v in sa("Net P&L"):
                running += v
                cum_pl_a.append(round(running, 3))

            cum_pl_b = []
            running = 0
            for v in sb("Net P&L"):
                running += v
                cum_pl_b.append(round(running, 3))

            fig_cum = go.Figure()
            if division in ["Both", "Amravati"]:
                fig_cum.add_trace(go.Scatter(
                    name="Amravati Cum. P&L", x=sel_months, y=cum_pl_a,
                    mode="lines+markers", line=dict(color="#3b82f6", width=2),
                    marker=dict(size=6), fill="tozeroy",
                    fillcolor="rgba(59,130,246,0.08)",
                ))
            if division in ["Both", "Betul"]:
                fig_cum.add_trace(go.Scatter(
                    name="Betul Cum. P&L", x=sel_months, y=cum_pl_b,
                    mode="lines+markers", line=dict(color="#8b5cf6", width=2, dash="dot"),
                    marker=dict(size=5),
                ))
            fig_cum.add_hline(y=0, line_width=1, line_color="#9ca3af", opacity=0.5)
            fig_cum.update_layout(**chart_layout("Cumulative Net P&L", height=330))
            st.plotly_chart(fig_cum, use_container_width=True)

    # Mini insight row
    if division in ["Both", "Amravati"] and metric == "Net P&L":
        profit_months = [(sel_months[i], v) for i, v in enumerate(sa("Net P&L")) if v >= 0]
        loss_months   = [(sel_months[i], v) for i, v in enumerate(sa("Net P&L")) if v < 0]
        ci1, ci2, ci3 = st.columns(3)
        ci1.info(f"✅ **Profitable months (A):** {len(profit_months)} — {', '.join([m for m,_ in profit_months]) or 'None'}")
        ci2.error(f"🔴 **Loss months (A):** {len(loss_months)}")
        worst_idx = sa("Net P&L").index(min(sa("Net P&L")))
        ci3.warning(f"⬇️ **Worst month (A):** {sel_months[worst_idx]} → {fmt_cr(sa('Net P&L')[worst_idx])}")

# ── TAB 2: Revenue vs Expenses ──
with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        gross = sa("Gross Sales")
        net   = sa("Net Sales")
        exps  = sa("Total Expenses")
        fig_re = go.Figure()
        fig_re.add_trace(go.Bar(name="Gross Sales", x=sel_months, y=gross,
                                marker_color="#3b82f6", opacity=0.9, marker_line_width=0))
        fig_re.add_trace(go.Bar(name="Total Expenses", x=sel_months, y=exps,
                                marker_color="#ef4444", opacity=0.8, marker_line_width=0))
        fig_re.add_trace(go.Scatter(name="Net Sales", x=sel_months, y=net,
                                    mode="lines+markers", line=dict(color="#22c55e", width=2),
                                    marker=dict(size=5)))
        fig_re.update_layout(**chart_layout("Revenue vs Expenses — Amravati", height=300))
        st.plotly_chart(fig_re, use_container_width=True)

    with col_r:
        # Amravati vs Betul Gross Sales grouped
        fig_div = go.Figure()
        fig_div.add_trace(go.Bar(name="Amravati", x=sel_months, y=sa("Gross Sales"),
                                  marker_color="#3b82f6", marker_line_width=0))
        fig_div.add_trace(go.Bar(name="Betul", x=sel_months, y=sb("Gross Sales"),
                                  marker_color="#f59e0b", marker_line_width=0, opacity=0.85))
        fig_div.update_layout(**chart_layout("Gross Sales — Division Comparison", height=300))
        st.plotly_chart(fig_div, use_container_width=True)

    # EBITDA line chart
    fig_ebitda = go.Figure()
    fig_ebitda.add_trace(go.Scatter(name="EBITDA (A)", x=sel_months, y=sa("EBITDA"),
                                     mode="lines+markers+text", line=dict(color="#3b82f6", width=2),
                                     marker=dict(size=7), text=[f"{v:.2f}" for v in sa("EBITDA")],
                                     textposition="top center", textfont=dict(size=9)))
    fig_ebitda.add_trace(go.Scatter(name="EBITDA (B)", x=sel_months, y=sb("EBITDA"),
                                     mode="lines+markers", line=dict(color="#8b5cf6", width=2, dash="dot"),
                                     marker=dict(size=6)))
    fig_ebitda.add_hline(y=0, line_width=1, line_color="#9ca3af", opacity=0.5)
    fig_ebitda.update_layout(**chart_layout("EBITDA Trend — Both Divisions", height=280))
    st.plotly_chart(fig_ebitda, use_container_width=True)

# ── TAB 3: Throughput & Fixed Costs ──
with tab3:
    col_l, col_r = st.columns(2)

    with col_l:
        through = sa("Throughput")
        fixed   = sa("Fixed Costs")
        t_colors = bar_colors(through, "#22c55e", "#ef4444")
        fig_t = go.Figure()
        fig_t.add_trace(go.Bar(name="Throughput", x=sel_months, y=through,
                                marker_color=t_colors, opacity=0.85, marker_line_width=0,
                                text=[f"{v:.2f}" for v in through],
                                textposition="outside", textfont=dict(size=9)))
        fig_t.add_trace(go.Scatter(name="Fixed Costs", x=sel_months, y=fixed,
                                    mode="lines+markers", line=dict(color="#ef4444", width=2, dash="dot"),
                                    marker=dict(size=6, color="#ef4444")))
        fig_t.add_hline(y=0, line_width=1, line_color="#9ca3af", opacity=0.4)
        fig_t.update_layout(**chart_layout("Throughput vs Fixed Costs (Amravati)", height=310))
        st.plotly_chart(fig_t, use_container_width=True)

    with col_r:
        # EBITDA Margin % bar
        margins_a = sa("EBITDA Margin %")
        margins_b = sb("EBITDA Margin %")
        fig_m = go.Figure()
        fig_m.add_trace(go.Bar(name="Amravati", x=sel_months, y=margins_a,
                                marker_color=bar_colors(margins_a, "#22c55e", "#ef4444"),
                                marker_line_width=0, opacity=0.9))
        fig_m.add_trace(go.Bar(name="Betul", x=sel_months, y=margins_b,
                                marker_color="#8b5cf6", marker_line_width=0, opacity=0.7))
        fig_m.add_hline(y=0, line_width=1, line_color="#9ca3af", opacity=0.5)
        fig_m.update_layout(**chart_layout("EBITDA Margin % — Both Divisions", height=310, y_suffix="%"))
        st.plotly_chart(fig_m, use_container_width=True)

    # Waterfall chart — Amravati YTD P&L bridge
    st.markdown("<div class='section-hdr'>YTD P&L Waterfall — Amravati</div>", unsafe_allow_html=True)
    ytd_rev   = sum(a["Gross Sales"][fr:to+1])
    ytd_cogs  = ytd_rev - sum(v for v in a["Throughput"][fr:to+1])
    ytd_tp    = sum(a["Throughput"][fr:to+1])
    ytd_fixed = sum(a["Fixed Costs"][fr:to+1])
    ytd_pl    = sum(a["Net P&L"][fr:to+1])

    wf_labels = ["Gross Sales", "COGS", "Throughput", "Fixed Costs", "Net P&L"]
    wf_vals   = [ytd_rev, -ytd_cogs, ytd_tp, -ytd_fixed, ytd_pl]
    wf_colors = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#16a34a" if ytd_pl >= 0 else "#dc2626"]

    fig_wf = go.Figure(go.Bar(
        x=wf_labels, y=wf_vals, marker_color=wf_colors, marker_line_width=0,
        text=[f"₹{v:.2f}Cr" for v in wf_vals], textposition="outside",
        textfont=dict(size=10),
    ))
    fig_wf.add_hline(y=0, line_width=1, line_color="#9ca3af", opacity=0.5)
    fig_wf.update_layout(**chart_layout("P&L Waterfall — Amravati (Selected Period)", height=280))
    st.plotly_chart(fig_wf, use_container_width=True)

# ── TAB 4: Detailed Table ──
with tab4:
    st.markdown("<div class='section-hdr'>Month-by-Month Breakdown</div>", unsafe_allow_html=True)

    show_div = division if division != "Both" else "Amravati"
    d_sel = a if show_div == "Amravati" else b
    sd = lambda k: slice_data(d_sel[k], fr, to)

    table_data = []
    for i, m in enumerate(sel_months):
        gs   = sd("Gross Sales")[i]
        ns   = sd("Net Sales")[i]
        pl   = sd("Net P&L")[i]
        eb   = sd("EBITDA")[i]
        em   = sd("EBITDA Margin %")[i]
        tp   = sd("Throughput")[i]
        fc   = sd("Fixed Costs")[i]
        te   = sd("Total Expenses")[i]
        table_data.append({
            "Month":              m,
            "Gross Sales (₹Cr)":  f"{gs:.3f}" if gs is not None else "—",
            "Net Sales (₹Cr)":    f"{ns:.3f}" if ns is not None else "—",
            "Total Expenses (₹Cr)":f"{te:.3f}" if te is not None else "—",
            "Net P&L (₹Cr)":      f"{pl:.3f}" if pl is not None else "—",
            "EBITDA (₹Cr)":       f"{eb:.3f}" if eb is not None else "—",
            "EBITDA Margin %":    f"{em:.1f}%" if em is not None else "—",
            "Throughput (₹Cr)":   f"{tp:.3f}" if tp is not None else "—",
            "Fixed Costs (₹Cr)":  f"{fc:.3f}" if fc is not None else "—",
        })

    if division == "Both":
        st.caption("ℹ️ Table shows Amravati data. Switch to Amravati/Betul in sidebar for respective view.")

    df = pd.DataFrame(table_data)

    def color_cell(val):
        try:
            raw = str(val).replace("₹","").replace("Cr","").replace("%","").replace("(","").replace(")","").strip()
            num = float(raw)
            if num > 0:  return "color: #16a34a; font-weight: 600"
            if num < 0:  return "color: #dc2626; font-weight: 600"
        except:
            pass
        return ""

    color_cols = ["Net P&L (₹Cr)", "EBITDA (₹Cr)", "EBITDA Margin %", "Throughput (₹Cr)"]
    try:
        styled = df.style.map(color_cell, subset=color_cols)
    except AttributeError:
        styled = df.style.applymap(color_cell, subset=color_cols)

    st.dataframe(styled, use_container_width=True, hide_index=True, height=420)

    # Summary totals row
    st.markdown("<div class='section-hdr'>Period Totals — " + show_div + "</div>", unsafe_allow_html=True)
    tot_gs = sum(v for v in sd("Gross Sales") if v)
    tot_pl = sum(v for v in sd("Net P&L") if v)
    tot_eb = sum(v for v in sd("EBITDA") if v)
    tot_te = sum(v for v in sd("Total Expenses") if v)
    tot_tp = sum(v for v in sd("Throughput") if v is not None)
    tot_fc = sum(v for v in sd("Fixed Costs") if v is not None)

    t1, t2, t3, t4, t5 = st.columns(5)
    t1.metric("Gross Sales",     fmt_cr(tot_gs))
    t2.metric("Total Expenses",  fmt_cr(tot_te))
    t3.metric("Net P&L",         fmt_cr(tot_pl), delta=f"{'▲' if tot_pl >= 0 else '▼'} vs breakeven")
    t4.metric("EBITDA",          fmt_cr(tot_eb))
    t5.metric("Throughput",      fmt_cr(tot_tp) if tot_tp else "—")

# ─────────────────────────────────────────────
st.markdown("---")
st.caption("Data source: Profit & Loss — Fashions Amravati & Betul, Feb 2026  ·  Built with Streamlit + Plotly")
