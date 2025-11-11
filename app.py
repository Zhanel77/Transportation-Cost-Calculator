# app.py
import streamlit as st
from least_cost_cell import (
    balance_problem,
    least_cost_method_with_steps,
    modi_optimize,
)

st.set_page_config(page_title="Transportation Demo", layout="wide")


st.markdown("""
<style>
/* ===== GENERAL PAGE STYLING ===== */
body {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 70%);
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}

/* ===== TITLES ===== */
h1, h2, h3, .app-title {
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.app-title {
    font-size: 2.2rem;
    color: #f8fafc;
    text-align: center;
    margin-bottom: 0.25rem;
}

.app-subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: #38bdf8;
    margin-bottom: 1.5rem;
}

/* ===== CARD / PANEL ===== */
.card {
    background: rgba(30, 41, 59, 0.55);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
}
.card:hover {
    border-color: rgba(56,189,248,0.5);
    box-shadow: 0 6px 20px rgba(56,189,248,0.25);
}

/* ===== INPUT LABELS ===== */
label, .stNumberInput label, .stTextInput label {
    color: #cbd5e1 !important;
    font-weight: 500;
}

/* ===== BUTTON ===== */
.stButton>button {
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
    color: #f8fafc;
    border: none;
    border-radius: 999px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    font-size: 0.95rem;
    box-shadow: 0 3px 10px rgba(56,189,248,0.4);
    transition: all 0.25s ease;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
    transform: translateY(-2px);
    box-shadow: 0 5px 14px rgba(56,189,248,0.6);
}

/* ===== TABLES ===== */
table {
    border-collapse: collapse;
    width: 100%;
}
thead th {
    background: rgba(30,41,59,0.9);
    color: #38bdf8;
    font-weight: 600;
    text-align: center;
    padding: 0.6rem;
}
tbody td {
    background: rgba(15,23,42,0.6);
    text-align: center;
    padding: 0.5rem;
    color: #e2e8f0;
}
tbody tr:hover td {
    background: rgba(56,189,248,0.1);
}

/* ===== STEP BOX ===== */
.step-box {
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 12px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.6rem;
    color: #e2e8f0;
    font-size: 0.9rem;
    transition: all 0.2s ease;
}
.step-box:hover {
    background: rgba(56,189,248,0.15);
}

/* ===== INFO BOX ===== */
.info-box {
    background: rgba(37,99,235,0.15);
    border: 1px solid rgba(59,130,246,0.35);
    border-radius: 12px;
    padding: 0.6rem 0.9rem;
    font-size: 0.88rem;
    color: #f1f5f9;
}

/* ===== CODE TEXT ===== */
code {
    background: rgba(15,23,42,0.35);
    color: #facc15;
    padding: 2px 6px;
    border-radius: 6px;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


st.markdown("## Transportation Problem – Demo")
st.write("Least Cost -> MODI")

col1, col2 = st.columns(2)
with col1:
    m = st.number_input("Sources (m)", 1, 10, 3)
with col2:
    n = st.number_input("Destinations (n)", 1, 10, 4)

# cost matrix
st.markdown('<div class="card">Cost matrix Cij</div>', unsafe_allow_html=True)
costs = []
for i in range(m):
    cols = st.columns(n)
    row = []
    for j in range(n):
        row.append(cols[j].number_input(f"c[{i+1},{j+1}]", 0, 9999, 1, key=f"c_{i}_{j}"))
    costs.append(row)

# supply / demand
st.markdown('<div class="card">Supply & Demand</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    supply = [st.number_input(f"supply[{i+1}]", 0, 9999, 10, key=f"s_{i}") for i in range(m)]
with c2:
    demand = [st.number_input(f"demand[{j+1}]", 0, 9999, 10, key=f"d_{j}") for j in range(n)]

if st.button("Solve transportation problem"):
    try:
        b_costs, b_supply, b_demand, dr, dc = balance_problem(costs, supply, demand)
    except ValueError as e:
        st.error(str(e))
    else:
        st.subheader("Balanced problem")
        st.table(b_costs)
        st.write("Supply:", b_supply)
        st.write("Demand:", b_demand)
        if dr: st.info("Dummy source was added")
        if dc: st.info("Dummy destination was added")

        alloc_lc, cost_lc, steps = least_cost_method_with_steps(b_costs, b_supply, b_demand)
        st.subheader("Least Cost – steps")
        for idx, stp in enumerate(steps, start=1):
            st.write(
                f"Step {idx}: choose (S{stp['cell'][0]}, D{stp['cell'][1]}) "
                f"cost={stp['cost']}, allocate {stp['allocated']}"
            )
        st.table(alloc_lc)
        st.write(f"Total cost: {cost_lc}")

        alloc_modi, cost_modi, modi_iters = modi_optimize(b_costs, alloc_lc)
        st.subheader("MODI optimization")
        if not modi_iters:
            st.write("No negative reduced costs → plan is optimal.")
        else:
            for it in modi_iters:
                st.write(it)
        st.table(alloc_modi)
        st.write(f"Final cost: {cost_modi}")
