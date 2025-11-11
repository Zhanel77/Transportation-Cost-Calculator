# transport_solver.py
from copy import deepcopy

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


# ====== MODI helpers ======

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
