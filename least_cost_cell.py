import streamlit as st
from copy import deepcopy

# =========== PAGE CONFIG ===========
st.set_page_config(page_title="Transportation Demo", layout="wide")

# =========== CUSTOM CSS ===========
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 55%);
}
.main .block-container {
    padding-top: 1.5rem;
}
.app-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #111827; 
    margin-bottom: .3rem;
}
.app-subtitle {
    color: #0f172a; 
    margin-bottom: 1.2rem;
}
h2.section-title {
    font-size: 1.1rem;
    color: #86a6d1; 
    margin-bottom: .6rem;
    font-weight: 700;
}
label, p, th, td, .stMarkdown, .stTextInput label, .stNumberInput label {
    color: #86a6d1 !important; 
}
.card {
    background: rgba(15,23,42,0.45);
    border: 1px solid rgba(148,163,184,.25);
    border-radius: 16px;
    padding: 1.1rem 1.25rem 1.15rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(12px);
}
.stButton>button {
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
    color: ##38bdf8;
    border: none;
    border-radius: 999px;
    padding: .45rem 1.4rem;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(56,189,248,0.35);
}
.step-box {
    background: rgba(30,41,59,0.4);
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 12px;
    padding: .55rem .8rem;
    margin-bottom: .5rem;
    font-size: .86rem;
    color: #1f2937;
}
.info-box {
    background: rgba(37,99,235,0.18);
    border: 1px solid rgba(59,130,246,0.35);
    border-radius: 12px;
    padding: .6rem .75rem;
    color: #1f2937;
    font-size: .82rem;
}
code {
    background: rgba(15,23,42,0.35);
    color: #1f2937; /* жёлтые цифры в коде */
    padding: 2px 6px;
    border-radius: 6px;
}
.stNumberInput label div {
    color: #1f2937 !important;
}
</style>
""", unsafe_allow_html=True)


# =========== TITLE ===========
st.markdown('<div class="app-title">Transportation Problem – Demo</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Least Cost → MODI</div>', unsafe_allow_html=True)

# =========== INPUTS ===========
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        m = st.number_input("Sources (m)", 1, 10, 3)
    with col2:
        n = st.number_input("Destinations (n)", 1, 10, 4)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Cost matrix cᵢⱼ</h2>', unsafe_allow_html=True)
costs = []
for i in range(m):
    cols = st.columns(n)
    row = []
    for j in range(n):
        row.append(cols[j].number_input(f"c[{i+1},{j+1}]", 0, 9999, 1, key=f"c_{i}_{j}"))
    costs.append(row)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Supply & Demand</h2>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    supply_cols = st.columns(m)
    supply = []
    for i in range(m):
        supply.append(supply_cols[i].number_input(f"supply[{i+1}]", 0, 9999, 10, key=f"s_{i}"))
with c2:
    demand_cols = st.columns(n)
    demand = []
    for j in range(n):
        demand.append(demand_cols[j].number_input(f"demand[{j+1}]", 0, 9999, 10, key=f"d_{j}"))
st.markdown('</div>', unsafe_allow_html=True)


# =========== ALGO FUNCTIONS ===========
def balance_problem(costs, supply, demand):
    costs = deepcopy(costs)
    supply = deepcopy(supply)
    demand = deepcopy(demand)
    sum_s = sum(supply)
    sum_d = sum(demand)
    dummy_row = False
    dummy_col = False
    if sum_s > sum_d:
        diff = sum_s - sum_d
        demand.append(diff)
        for r in costs:
            r.append(0)
        dummy_col = True
    elif sum_d > sum_s:
        diff = sum_d - sum_s
        supply.append(diff)
        costs.append([0] * len(demand))
        dummy_row = True
    return costs, supply, demand, dummy_row, dummy_col


def least_cost_method_with_steps(costs, supply, demand):
    costs = deepcopy(costs)
    supply = deepcopy(supply)
    demand = deepcopy(demand)
    m = len(supply)
    n = len(demand)
    alloc = [[0] * n for _ in range(m)]
    cells = [(costs[i][j], i, j) for i in range(m) for j in range(n)]
    cells.sort()
    steps = []
    for cost, i, j in cells:
        if supply[i] == 0 or demand[j] == 0:
            continue
        qty = min(supply[i], demand[j])
        alloc[i][j] = qty
        steps.append({
            "cell": (i+1, j+1),
            "cost": cost,
            "allocated": qty,
            "s_rem": supply[i] - qty,
            "d_rem": demand[j] - qty
        })
        supply[i] -= qty
        demand[j] -= qty
    total_cost = sum(alloc[i][j] * costs[i][j] for i in range(m) for j in range(n))
    return alloc, total_cost, steps


def compute_potentials(costs, alloc):
    m = len(costs)
    n = len(costs[0])
    u = [None] * m
    v = [None] * n
    u[0] = 0
    changed = True
    while changed:
        changed = False
        for i in range(m):
            for j in range(n):
                if alloc[i][j] > 0:
                    if u[i] is not None and v[j] is None:
                        v[j] = costs[i][j] - u[i]
                        changed = True
                    elif v[j] is not None and u[i] is None:
                        u[i] = costs[i][j] - v[j]
                        changed = True
    return u, v


def find_most_negative(costs, alloc, u, v):
    m = len(costs)
    n = len(costs[0])
    best_cell = None
    best_delta = 0
    for i in range(m):
        for j in range(n):
            if alloc[i][j] == 0:
                if u[i] is None or v[j] is None:
                    continue
                delta = costs[i][j] - (u[i] + v[j])
                if delta < best_delta:
                    best_delta = delta
                    best_cell = (i, j)
    return best_cell, best_delta


def find_loop(allocation, si, sj):
    m = len(allocation)
    n = len(allocation[0])
    start = (si, sj)
    occupied = [(i, j) for i in range(m) for j in range(n) if allocation[i][j] > 0]
    if start not in occupied:
        occupied.append(start)
    path = [start]

    def dfs(cell, used, by_row):
        i, j = cell
        if by_row:
            for jj in range(n):
                nxt = (i, jj)
                if nxt == cell or nxt not in occupied:
                    continue
                if nxt == start and len(path) >= 4 and len(path) % 2 == 0:
                    return True
                if nxt in used:
                    continue
                used.add(nxt); path.append(nxt)
                if dfs(nxt, used, not by_row): return True
                path.pop(); used.remove(nxt)
        else:
            for ii in range(m):
                nxt = (ii, j)
                if nxt == cell or nxt not in occupied:
                    continue
                if nxt == start and len(path) >= 4 and len(path) % 2 == 0:
                    return True
                if nxt in used:
                    continue
                used.add(nxt); path.append(nxt)
                if dfs(nxt, used, not by_row): return True
                path.pop(); used.remove(nxt)
        return False

    dfs(start, {start}, True)
    return path


def apply_loop(allocation, loop):
    minus_cells = loop[1::2]
    theta = min(allocation[i][j] for (i, j) in minus_cells)
    for idx, (i, j) in enumerate(loop):
        if idx % 2 == 0:
            allocation[i][j] += theta
        else:
            allocation[i][j] -= theta
    return allocation, theta


def modi_optimize(costs, alloc):
    alloc = deepcopy(alloc)
    iterations = []
    while True:
        u, v = compute_potentials(costs, alloc)
        cell, delta = find_most_negative(costs, alloc, u, v)
        if cell is None or delta >= 0:
            break
        si, sj = cell
        loop = find_loop(alloc, si, sj)
        if not loop or len(loop) < 4:
            break
        alloc, theta = apply_loop(alloc, loop)
        iterations.append({
            "entering": (si+1, sj+1),
            "delta": delta,
            "theta": theta,
            "loop": [(i+1, j+1) for (i, j) in loop]
        })
    total = sum(
        alloc[i][j] * costs[i][j]
        for i in range(len(costs))
        for j in range(len(costs[0]))
    )
    return alloc, total, iterations


# =========== SOLVE BUTTON ===========
if st.button("Solve transportation problem"):
    b_costs, b_supply, b_demand, dr, dc = balance_problem(costs, supply, demand)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Balanced problem</h2>', unsafe_allow_html=True)
    st.write("Cost matrix:")
    st.table(b_costs)
    st.write(f"Supply: {b_supply}")
    st.write(f"Demand: {b_demand}")
    if dr:
        st.markdown('<div class="info-box">Dummy source was added</div>', unsafe_allow_html=True)
    if dc:
        st.markdown('<div class="info-box">Dummy destination was added</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    alloc_lc, cost_lc, steps = least_cost_method_with_steps(b_costs, b_supply, b_demand)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Least Cost – steps</h2>', unsafe_allow_html=True)
    for idx, stp in enumerate(steps, start=1):
        st.markdown(
            f'<div class="step-box"><b>Step {idx}</b>: choose cell (S{stp["cell"][0]}, D{stp["cell"][1]}) '
            f'with cost <code>{stp["cost"]}</code>, allocate <b>{stp["allocated"]}</b> '
            f'(supply→ {stp["s_rem"]}, demand→ {stp["d_rem"]})</div>',
            unsafe_allow_html=True
        )
    st.write("Allocation (Least Cost):")
    st.table(alloc_lc)
    st.write(f"Total cost: **{cost_lc}**")
    st.markdown('</div>', unsafe_allow_html=True)

    alloc_modi, cost_modi, modi_iters = modi_optimize(b_costs, alloc_lc)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">MODI optimization</h2>', unsafe_allow_html=True)
    if not modi_iters:
        st.write("No negative reduced costs → plan is (locally) optimal.")
    else:
        for i, it in enumerate(modi_iters, start=1):
            st.markdown(
                f'<div class="step-box"><b>Iter {i}</b>: enter (S{it["entering"][0]}, D{it["entering"][1]}), '
                f'Δ = {it["delta"]:.2f}, θ = {it["theta"]}, loop = {it["loop"]}</div>',
                unsafe_allow_html=True
            )
    st.write("Final allocation:")
    st.table(alloc_modi)
    st.write(f"Final cost: **{cost_modi}**")
    st.markdown('</div>', unsafe_allow_html=True)
