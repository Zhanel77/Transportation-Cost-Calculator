from copy import deepcopy

# -------- 1. balance --------
def check_balance(supply, demand):
    if sum(supply) != sum(demand):
        raise ValueError(
            f"Unbalanced transportation problem: total supply = {sum(supply)}, "
            f"total demand = {sum(demand)}. They must be equal."
        )

# -------- 2. least cost --------
def least_cost_initial(costs, supply, demand):
    costs = deepcopy(costs)
    s = deepcopy(supply)
    d = deepcopy(demand)
    m, n = len(s), len(d)

    alloc = [[0.0]*n for _ in range(m)]
    steps = []

    cells = [(costs[i][j], i, j) for i in range(m) for j in range(n)]
    cells.sort()

    for c, i, j in cells:
        if s[i] == 0 or d[j] == 0:
            continue
        qty = min(s[i], d[j])
        alloc[i][j] = float(qty)
        steps.append({
            "step": len(steps)+1,
            "cell": (i+1, j+1),
            "cost": c,
            "allocated": qty,
            "supply_after": s[i] - qty,
            "demand_after": d[j] - qty
        })
        s[i] -= qty
        d[j] -= qty

    occupied = sum(1 for i in range(m) for j in range(n) if alloc[i][j] > 0)
    expected = m + n - 1
    total_cost = sum(alloc[i][j]*costs[i][j] for i in range(m) for j in range(n))

    return alloc, total_cost, steps, occupied, expected

# -------- 3. MODI (оставляем как есть) --------
def compute_potentials(costs, alloc):
    m, n = len(costs), len(costs[0])
    u = [None]*m
    v = [None]*n
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

def find_largest_positive_w(costs, alloc, u, v):
    m, n = len(costs), len(costs[0])
    best_cell = None
    best_w = 0
    for i in range(m):
        for j in range(n):
            if alloc[i][j] == 0:
                if u[i] is None or v[j] is None:
                    continue
                w = u[i] + v[j] - costs[i][j]
                if w > best_w:
                    best_w = w
                    best_cell = (i, j)
    return best_cell, best_w

def find_loop(allocation, si, sj):
    m, n = len(allocation), len(allocation[0])
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
        cell, w_max = find_largest_positive_w(costs, alloc, u, v)
        if cell is None or w_max <= 0:
            break
        si, sj = cell
        loop = find_loop(alloc, si, sj)
        if not loop or len(loop) < 4:
            break
        alloc, theta = apply_loop(alloc, loop)
        iterations.append({
            "entering": (si+1, sj+1),
            "w": float(w_max),
            "theta": theta,
            "loop": [(i+1, j+1) for (i, j) in loop]
        })

    total = sum(
        alloc[i][j] * costs[i][j]
        for i in range(len(costs))
        for j in range(len(costs[0]))
        if alloc[i][j] > 0
    )
    return alloc, total, iterations

# -------- 4. high-level --------
def solve_transportation(costs, supply, demand):
    # 1) balance
    check_balance(supply, demand)

    # 2) initial solution
    alloc_lc, cost_lc, steps_lc, occupied, expected = least_cost_initial(
        costs, supply, demand
    )

    # 3) если вырождено — просто вернуть и не запускать MODI
    if occupied < expected:
        return {
            "least_cost_allocation": alloc_lc,
            "least_cost": cost_lc,
            "least_cost_steps": steps_lc,
            "is_degenerate": True,
            "expected_basic_cells": expected,
            "modi_allocation": None,
            "modi_cost": None,
            "modi_steps": [],
        }

    # 4) иначе запускаем MODI
    alloc_opt, cost_opt, modi_steps = modi_optimize(costs, alloc_lc)
    return {
        "least_cost_allocation": alloc_lc,
        "least_cost": cost_lc,
        "least_cost_steps": steps_lc,
        "is_degenerate": False,
        "expected_basic_cells": expected,
        "modi_allocation": alloc_opt,
        "modi_cost": cost_opt,
        "modi_steps": modi_steps,
    }