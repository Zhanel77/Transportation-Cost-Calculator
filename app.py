import streamlit as st
import pandas as pd
from least_cost_cell import solve_transportation   # твой файл с алгоритмом

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Transportation Problem – Demo", layout="wide")

# -------------------------------------------------
# SIMPLE STYLE
# -------------------------------------------------
st.markdown(
    """
    <style>
    .card {
        background: #f3f4f6;
        padding: 1rem 1.2rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
    .step-box {
        background: #e2e8f0;
        padding: .45rem .75rem;
        border-radius: .6rem;
        margin-bottom: .4rem;
        font-size: .9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("TRANSPORTATION PROBLEM – DEMO")
st.write("Least Cost → MODI")

# -------------------------------------------------
# 1. INPUTS
# -------------------------------------------------
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        m = st.number_input("Sources (m)", min_value=1, max_value=10, value=3)
    with col2:
        n = st.number_input("Destinations (n)", min_value=1, max_value=10, value=4)

# ---- cost matrix ----
st.markdown('<div class="card"><h4>Cost matrix cᵢⱼ</h4>', unsafe_allow_html=True)
costs = []
for i in range(m):
    row_cols = st.columns(n)
    row = []
    for j in range(n):
        val = row_cols[j].number_input(
            f"c[{i+1},{j+1}]",
            min_value=0,
            value=1,
            key=f"c_{i}_{j}",
        )
        row.append(val)
    costs.append(row)
st.markdown("</div>", unsafe_allow_html=True)

# ---- supply & demand ----
st.markdown('<div class="card"><h4>Supply & Demand</h4>', unsafe_allow_html=True)
col_s, col_d = st.columns(2)

supply = []
with col_s:
    for i in range(m):
        supply.append(
            st.number_input(
                f"supply[{i+1}]",
                min_value=0,
                value=10,
                key=f"s_{i}",
            )
        )

demand = []
with col_d:
    for j in range(n):
        demand.append(
            st.number_input(
                f"demand[{j+1}]",
                min_value=0,
                value=10,
                key=f"d_{j}",
            )
        )

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 2. SOLVE
# -------------------------------------------------
if st.button("Solve transportation problem"):
    try:
        result = solve_transportation(costs, supply, demand)
    except ValueError as e:
        st.error(str(e))
    else:
        # ---------- BALANCED PROBLEM ----------
        st.markdown('<div class="card"><h4>Balanced problem</h4>', unsafe_allow_html=True)
        st.write("Cost matrix:")
        st.table(pd.DataFrame(costs))
        st.write(f"Supply: {supply}")
        st.write(f"Demand: {demand}")
        st.markdown("</div>", unsafe_allow_html=True)

        # ---------- LEAST COST ----------
        st.markdown('<div class="card"><h4>Least Cost – steps</h4>', unsafe_allow_html=True)
        lc_steps = result["least_cost_steps"]
        for stp in lc_steps:
            st.markdown(
                f'<div class="step-box">'
                f'<b>Step {stp["step"]}</b>: choose cell (S{stp["cell"][0]}, D{stp["cell"][1]}) '
                f'with cost <code>{stp["cost"]}</code>, allocate <b>{stp["allocated"]}</b> '
                f'(supply → {stp["supply_after"]}, demand → {stp["demand_after"]})'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.write("Allocation (Least Cost):")
        df_lc = pd.DataFrame(result["least_cost_allocation"])

        # аккуратное форматирование без FutureWarning
        df_lc = df_lc.apply(
            lambda col: col.map(lambda x: int(x) if float(x).is_integer() else round(x, 2))
        )
        st.table(df_lc)
        st.write(f"Total cost (Least Cost): **{int(result['least_cost'])}**")

        # ---------- DEGENERACY CHECK ----------
        if result["is_degenerate"]:
            st.warning(
                "Degenerate basic feasible solution: occupied cells < m + n − 1. "
                "In this project we stop after the initial plan and do not run MODI."
            )
            # тут просто НЕ показываем MODI и выходим
        else:
            st.success(
                "Non-degenerate solution: number of occupied cells = m + n − 1 "
                f"({result['expected_basic_cells']})."
            )

            # ---------- MODI ----------
            st.markdown('<div class="card"><h4>MODI optimization</h4>', unsafe_allow_html=True)

            modi_steps = result["modi_steps"]
            if not modi_steps:
                st.write("All wᵢⱼ ≤ 0 → current solution is optimal.")
            else:
                for idx, it in enumerate(modi_steps, start=1):
                    st.markdown(
                        f'<div class="step-box"><b>Iter {idx}</b>: '
                        f'enter (S{it["entering"][0]}, D{it["entering"][1]}), '
                        f'w = {it["w"]:.2f}, '
                        f'θ = {it["theta"]}, '
                        f'loop = {it["loop"]}</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown("</div>", unsafe_allow_html=True)

            st.write("Final allocation (after MODI):")
            df_modi = pd.DataFrame(result["modi_allocation"])
            df_modi = df_modi.apply(
                lambda col: col.map(lambda x: int(x) if float(x).is_integer() else round(x, 2))
            )
            st.table(df_modi)
            st.write(f"Final cost: **{int(result['modi_cost'])}**")

else:
    st.info("Enter data above and press the button to solve.")
