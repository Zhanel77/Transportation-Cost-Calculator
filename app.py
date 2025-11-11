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
body { background: radial-gradient(circle at top, #0f172a 0%, #020617 55%); }
.stButton>button {
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
    color: white;
    border: none; border-radius: 999px;
    padding: .45rem 1.4rem; font-weight: 600;
}
.card { background: rgba(15,23,42,0.45); border-radius: 16px; padding: 1rem 1.25rem; }
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
    b_costs, b_supply, b_demand, dr, dc = balance_problem(costs, supply, demand)

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
