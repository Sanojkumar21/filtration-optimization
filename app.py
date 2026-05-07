"""
Streamlit Dashboard: Module 1.3 — Fixed-Bed Filtration Optimization
"""
import streamlit as st
import numpy as np
from scipy.optimize import minimize
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Filtration Optimization", layout="wide",
                   page_icon="🧪")

# ── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stMetric {background: linear-gradient(135deg, #1a1a2e, #16213e);
               padding: 15px; border-radius: 12px; border: 1px solid #30475e;}
    h1 {color: #e94560; text-align: center;}
    h2, h3 {color: #0f9ef7;}
</style>
""", unsafe_allow_html=True)

st.title("🧪 Fixed-Bed Filtration Economic Optimization")
st.markdown("**Module 1.3** — Optimize filtration rate and run volume to minimize total annual cost")

# ── Sidebar: Parameters ────────────────────────────────────────
st.sidebar.header("⚙️ System Parameters")

Qp = st.sidebar.number_input("Plant capacity Qₚ (m³/day)", 1000, 100000, 10000, 500)
T_op = st.sidebar.slider("Operating time Tₒₚ (h/day)", 10.0, 24.0, 20.0, 0.5)
t_w = st.sidebar.slider("Backwash duration tᵥ (h)", 0.1, 2.0, 0.5, 0.1)
v_w = st.sidebar.slider("Backwash volume vᵥ (m³/m²)", 0.05, 0.50, 0.15, 0.01)

st.sidebar.header("🔬 Head-Loss Parameters")
alpha = st.sidebar.slider("Clean-bed coeff α (m·h/m)", 0.05, 1.0, 0.30, 0.01)
beta = st.sidebar.slider("Development rate β (m·h/m³)", 0.001, 0.050, 0.008, 0.001,
                          format="%.3f")
H_a = st.sidebar.slider("Available head Hₐ (m)", 1.0, 10.0, 3.0, 0.1)

st.sidebar.header("💰 Economic Parameters")
Ce = st.sidebar.slider("Electricity price ($/kWh)", 0.02, 0.30, 0.10, 0.01)
a_c = st.sidebar.slider("Construction cost ($/m²)", 100, 2000, 500, 50)
i_rate = st.sidebar.slider("Interest rate", 0.03, 0.15, 0.08, 0.01)
n_life = st.sidebar.slider("Plant life (years)", 5, 40, 20, 1)
c_w = st.sidebar.slider("Backwash water cost ($/m³)", 0.1, 2.0, 0.5, 0.1)
rho = 1000.0
g_acc = 9.81
eta_p = st.sidebar.slider("Pump efficiency η", 0.50, 0.95, 0.75, 0.01)

# ── Calculations ───────────────────────────────────────────────
CRF = i_rate * (1 + i_rate)**n_life / ((1 + i_rate)**n_life - 1)
a_coeff = CRF * a_c / T_op
e_coeff = CRF * a_c * t_w / T_op + 365 * c_w * v_w
b_coeff = 365 * Ce * rho * g_acc / (1000 * eta_p)


def total_cost(v, Vf):
    return (a_coeff / v + e_coeff / Vf
            + b_coeff * alpha * v + 0.5 * b_coeff * beta * v * Vf)

def head_loss(v, Vf):
    return alpha * v + beta * v * Vf

def cost_scipy(x):
    return total_cost(x[0], x[1]) * Qp

# Unconstrained
bounds = [(1.0, 30.0), (10.0, 1000.0)]
res_unc = minimize(cost_scipy, [8, 200], method='L-BFGS-B', bounds=bounds)
v_unc, Vf_unc = res_unc.x
C_unc = res_unc.fun
hT_unc = head_loss(v_unc, Vf_unc)

# Constrained
con = {'type': 'ineq', 'fun': lambda x: H_a - head_loss(x[0], x[1])}
res_con = minimize(cost_scipy, [8, 200], method='SLSQP', bounds=bounds, constraints=con)
v_con, Vf_con = res_con.x
C_con = res_con.fun
hT_con = head_loss(v_con, Vf_con)

# ── Results Display ────────────────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("CRF", f"{CRF:.4f}")
col2.metric("a (capital)", f"{a_coeff:.2f}")
col3.metric("b (energy)", f"{b_coeff:.4f}")

st.markdown("## 📊 Optimization Results")
tab1, tab2 = st.tabs(["Unconstrained", "Constrained (Letterman)"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("v* (m/h)", f"{v_unc:.3f}")
    c2.metric("Vf* (m³/m²)", f"{Vf_unc:.1f}")
    c3.metric("Cost ($/yr)", f"${C_unc:,.0f}")
    c4.metric("h_T (m)", f"{hT_unc:.3f}")
    tr = Vf_unc / v_unc
    nc = T_op / (tr + t_w)
    Ar = Qp / (nc * Vf_unc)
    c5, c6, c7 = st.columns(3)
    c5.metric("Run time (h)", f"{tr:.2f}")
    c6.metric("Cycles/day", f"{nc:.2f}")
    c7.metric("Filter area (m²)", f"{Ar:.1f}")

with tab2:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("v* (m/h)", f"{v_con:.3f}")
    c2.metric("Vf* (m³/m²)", f"{Vf_con:.1f}")
    c3.metric("Cost ($/yr)", f"${C_con:,.0f}")
    c4.metric("h_T (m)", f"{hT_con:.3f}")
    tr_c = Vf_con / v_con
    nc_c = T_op / (tr_c + t_w)
    Ar_c = Qp / (nc_c * Vf_con)
    c5, c6, c7 = st.columns(3)
    c5.metric("Run time (h)", f"{tr_c:.2f}")
    c6.metric("Cycles/day", f"{nc_c:.2f}")
    c7.metric("Filter area (m²)", f"{Ar_c:.1f}")
    pct = (C_con - C_unc) / C_unc * 100
    if pct > 0.01:
        st.warning(f"Constraint active — cost increase: **{pct:.2f}%**")
    else:
        st.success("Constraint inactive — same as unconstrained solution")

# ── Plot 1: Cost Contour ───────────────────────────────────────
st.markdown("## 🗺️ Cost Landscape")

v_range = np.linspace(1, 25, 150)
Vf_range = np.linspace(10, 600, 150)
V, VF = np.meshgrid(v_range, Vf_range)
Z = total_cost(V, VF) * Qp

fig = make_subplots(rows=1, cols=2, subplot_titles=[
    "Cost Contour with Constraint", "Sensitivity to Available Head Hₐ"],
    horizontal_spacing=0.12)

fig.add_trace(go.Contour(
    z=Z, x=v_range, y=Vf_range,
    colorscale='Viridis', ncontours=25,
    contours=dict(showlabels=True, labelfont=dict(size=9)),
    colorbar=dict(title="$/yr", x=0.45),
    showscale=True
), row=1, col=1)

# Constraint boundary
v_bnd = np.linspace(0.5, H_a / alpha - 0.1, 200)
Vf_bnd = (H_a - alpha * v_bnd) / (beta * v_bnd)
fig.add_trace(go.Scatter(x=v_bnd, y=Vf_bnd, mode='lines',
    line=dict(color='red', width=3), name=f'h_T = Hₐ = {H_a}m'), row=1, col=1)

fig.add_trace(go.Scatter(x=[v_unc], y=[Vf_unc], mode='markers',
    marker=dict(size=14, color='white', symbol='star', line=dict(width=2, color='black')),
    name='Unconstrained'), row=1, col=1)
fig.add_trace(go.Scatter(x=[v_con], y=[Vf_con], mode='markers',
    marker=dict(size=14, color='red', symbol='star', line=dict(width=2, color='black')),
    name='Constrained'), row=1, col=1)

# Sensitivity
H_vals = np.linspace(1.5, 8.0, 40)
costs_h = []
for h in H_vals:
    con_h = {'type': 'ineq', 'fun': lambda x, hh=h: hh - head_loss(x[0], x[1])}
    r = minimize(cost_scipy, [v_con, Vf_con], method='SLSQP', bounds=bounds, constraints=con_h)
    costs_h.append(r.fun)

fig.add_trace(go.Scatter(x=H_vals, y=costs_h, mode='lines+markers',
    line=dict(color='#e94560', width=2), marker=dict(size=5),
    name='Constrained cost', showlegend=False), row=1, col=2)
fig.add_trace(go.Scatter(x=H_vals, y=[C_unc]*len(H_vals), mode='lines',
    line=dict(color='#0f9ef7', dash='dash', width=2),
    name='Unconstrained', showlegend=False), row=1, col=2)

fig.update_xaxes(title_text="v (m/h)", row=1, col=1)
fig.update_yaxes(title_text="Vf (m³/m²)", row=1, col=1)
fig.update_xaxes(title_text="Hₐ (m)", row=1, col=2)
fig.update_yaxes(title_text="Cost ($/yr)", row=1, col=2)
fig.update_layout(height=500, template='plotly_dark',
                  margin=dict(t=40, b=40), legend=dict(x=0.01, y=0.99))
st.plotly_chart(fig, use_container_width=True)

# ── Plot 2: Cost Breakdown ─────────────────────────────────────
st.markdown("## 📊 Cost Breakdown")

scenarios = ['Unconstrained', 'Constrained']
cap_vals, en_vals, bw_vals = [], [], []
for vi, vfi in [(v_unc, Vf_unc), (v_con, Vf_con)]:
    cap = (a_coeff / vi + CRF * a_c * t_w / T_op / vfi) * Qp
    en = (b_coeff * alpha * vi + 0.5 * b_coeff * beta * vi * vfi) * Qp
    bw = 365 * c_w * v_w / vfi * Qp
    cap_vals.append(cap)
    en_vals.append(en)
    bw_vals.append(bw)

fig2 = go.Figure()
fig2.add_trace(go.Bar(x=scenarios, y=cap_vals, name='Capital',
                       marker_color='#4361ee'))
fig2.add_trace(go.Bar(x=scenarios, y=en_vals, name='Energy',
                       marker_color='#f72585'))
fig2.add_trace(go.Bar(x=scenarios, y=bw_vals, name='Backwash',
                       marker_color='#4cc9f0'))
fig2.update_layout(barmode='stack', template='plotly_dark', height=400,
                   yaxis_title='Annual Cost ($/yr)',
                   title='Cost Breakdown Comparison')
st.plotly_chart(fig2, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("*Module 1.3 — Sanoj Kumar (2022CH11454) | CLL782 Optimization Project*")
