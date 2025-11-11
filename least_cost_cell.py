# transport_solver.py
from copy import deepcopy

EPS = 1e-6  # используется для устранения вырожденности


# ---------- 1. BALANCE CHECK ----------
def check_balance(supply, demand):
    """Check ∑a_i = ∑b_j. Raise if not balanced."""
    sum_s = sum(supply)
    sum_d = sum(demand)
    if sum_s != sum_d:
        raise ValueError(
            f"Unbalanced transportation problem: total supply = {sum_s}, "
            f"total demand = {sum_d}. They must be equal for a feasible solution."
        )
    return True


# ---------- 2. LEAST COST (INITIAL BASIC FEASIBLE SOLUTION) ----------
def least_cost_initial(costs, supply, demand):
    """
    Matrix-minima / Least-cost entry method.
    Returns:
        alloc        - allocation matrix
        total_cost   - cost of this initial plan
        steps        - list of step descriptions
        occupied     - number of strictly positive allocations
        expected     - m + n - 1
    """
    costs = deepcopy(costs)
    s = deepcopy(supply)
    d = deepcopy(demand)
    m = len(s)
    n = len(d)

    alloc = [[0.0] * n for _ in range(m)]
    steps = []

    # list of all cells sorted by cost
    cells = [(costs[i][j], i, j) for i in range(m) for j in range(n)]
    cells.sort()  # ascending by cost

    for cost, i, j in cells:
        if s[i] == 0 or d[j] == 0:
            continue
        qty = min(s[i], d[j])
        alloc[i][j] = float(qty)
        steps.append(
            {
                "step": len(steps) + 1,
                "cell": (i + 1, j + 1),  # 1-based
                "cost": cost,
                "allocated": qty,
                "supply_after": s[i] - qty,
                "demand_after": d[j] - qty,
            }
        )
        s[i] -= qty
        d[j] -= qty

    # count strictly positive allocations
    occupied = sum(1 for i in range(m) for j in range(n) if alloc[i][j] > 0)
    expected = m + n - 1

    # compute cost
    total_cost = sum(
        alloc[i][j] * costs[i][j] for i in range(m) for j in range(n)
    )

    return alloc, total_cost, steps, occupied, expected


# ---------- 3. DEGENERACY FIX ----------
def fix_degeneracy(alloc, occupied, expected):
    """
    If occupied < expected, add tiny eps to some zero cells
    to make the solution a basic feasible solution.
    """
    if occupied >= expected:
        return alloc, False  # nothing to fix

    m = len(alloc)
    n = len(alloc[0])

    # walk through cells and add eps to empty ones until we reach expected
    for i in range(m):
        for j in range(n):
            if alloc[i][j] == 0:
                alloc[i][j] = EPS
                occupied += 1
                if occupied == expected:
                    return alloc, True

    # theoretically мы сюда не дойдём
    return alloc, True


# ---------- 4. MODI HELPERS ----------
def compute_potentials(costs, alloc):
    """
    Compute u_i and v_j from occupied cells (alloc > 0 or ≈EPS).
    """
    m = len(costs)
    n = len(costs[0])
    u = [None] * m
    v = [None] * n

    u[0] = 0  # fix reference
    changed = True
    while changed:
        changed = False
        for i in range(m):
            for j in range(n):
                if alloc[i][j] > 0:  # treat eps as occupied
                    if u[i] is not None and v[j] is None:
                        v[j] = costs[i][j] - u[i]
                        changed = True
                    elif v[j] is not None and u[i] is None:
                        u[i] = costs[i][j] - v[j]
                        changed = True
    return u, v


def find_most_negative(costs, alloc, u, v):
    """
    Find the non-basic cell with the most negative reduced cost.
    """
    m = len(costs)
    n = len(costs[0])
    best_cell = None
    best_delta = 0  # we look for delta < 0

    for i in range(m):
        for j in range(n):
            if alloc[i][j] == 0:  # only non-basic
                if u[i] is None or v[j] is None:
                    continue
                delta = costs[i][j] - (u[i] + v[j])
                if delta < best_delta:
                    best_delta = delta
                    best_cell = (i, j)
    return best_cell, best_delta


def find_loop(allocation, si, sj):
    """
    Build the closed path for MODI starting at (si, sj).
    DFS alternates between row/column.
    """
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
            # move in row
            for jj in range(n):
                nxt = (i, jj)
                if nxt == cell or nxt not in occupied:
                    continue
                if nxt == start and len(path) >= 4 and len(path) % 2 == 0:
                    return True
                if nxt in used:
                    continue
                used.add(nxt)
                path.append(nxt)
                if dfs(nxt, used, not by_row):
                    return True
                path.pop()
                used.remove(nxt)
        else:
            # move in column
            for ii in range(m):
                nxt = (ii, j)
                if nxt == cell or nxt not in occupied:
                    continue
                if nxt == start and len(path) >= 4 and len(path) % 2 == 0:
                    return True
                if nxt in used:
                    continue
                used.add(nxt)
                path.append(nxt)
                if dfs(nxt, used, not by_row):
                    return True
                path.pop()
                used.remove(nxt)
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


# 5. MODI MAIN 
def find_largest_positive_w(costs, alloc, u, v):
    """
    Textbook MODI: w_ij = u_i + v_j - c_ij
    Если все w_ij <= 0 -> оптимально.
    Иначе берём клетку с максимальным w_ij.
    """
    m = len(costs)
    n = len(costs[0])
    best_cell = None
    best_w = 0  # ищем w > 0

    for i in range(m):
        for j in range(n):
            if alloc[i][j] == 0:  # только свободные клетки
                if u[i] is None or v[j] is None:
                    continue
                w = u[i] + v[j] - costs[i][j]
                if w > best_w:      # ищем максимальный положительный
                    best_w = w
                    best_cell = (i, j)

    return best_cell, best_w


def modi_optimize(costs, alloc):
    """
    MODI по схеме из конспекта:
    1) считаем u, v
    2) считаем w_ij = u_i + v_j - c_ij
    3) если все w_ij <= 0 -> оптимум
    4) иначе берём ячейку с max w_ij и строим цикл
    """
    alloc = deepcopy(alloc)
    iterations = []

    while True:
        # шаг (i): potentials
        u, v = compute_potentials(costs, alloc)

        # шаг (ii) и (iii): net evaluations w_ij
        cell, w_max = find_largest_positive_w(costs, alloc, u, v)

        # если нет положительного w -> оптимум
        if cell is None or w_max <= 0:
            break

        si, sj = cell

        # строим замкнутый путь, как обычно
        loop = find_loop(alloc, si, sj)
        if not loop or len(loop) < 4:
            # теоретически не должно случиться, но на всякий случай
            break

        # θ – минимум по минусовым клеткам
        alloc, theta = apply_loop(alloc, loop)

        iterations.append(
            {
                "entering": (si + 1, sj + 1),
                "w": float(w_max),
                "theta": theta,
                "loop": [(i + 1, j + 1) for (i, j) in loop],
            }
        )

    # финальная стоимость
    total = sum(
        alloc[i][j] * costs[i][j]
        for i in range(len(costs))
        for j in range(len(costs[0]))
        if alloc[i][j] > EPS
    )

    return alloc, total, iterations
# ---------- 6. HIGH-LEVEL SOLVER (для Streamlit) ----------
def solve_transportation(costs, supply, demand):

    # 1. balance
    check_balance(supply, demand)

    # 2. initial solution
    alloc_lc, cost_lc, steps_lc, occupied, expected = least_cost_initial(
        costs, supply, demand
    )

    # 3. degeneracy
    was_degenerate = occupied < expected
    if was_degenerate:
        alloc_fixed, fixed = fix_degeneracy(alloc_lc, occupied, expected)
    else:
        alloc_fixed = alloc_lc

    # 4. MODI
    alloc_opt, cost_opt, modi_steps = modi_optimize(costs, alloc_fixed)

    return {
        "least_cost_allocation": alloc_lc,
        "least_cost": cost_lc,
        "least_cost_steps": steps_lc,
        "is_degenerate": was_degenerate,
        "expected_basic_cells": expected,
        "modi_allocation": alloc_opt,
        "modi_cost": cost_opt,
        "modi_steps": modi_steps,
    }
