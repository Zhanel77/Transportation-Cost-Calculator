from least_cost_cell import (
    check_balance,
    least_cost_initial,
    fix_degeneracy,
    modi_optimize,
)

def main():
    # 1. исходные данные (как в твоём streamlit)
    costs = [
        [5, 6, 8, 9],
        [8, 4, 7, 5],
        [5, 8, 3, 10],
    ]
    supply = [45, 35, 18]
    demand = [26, 26, 10, 36]

    print("== Transportation Problem ==")
    print("Cost matrix:")
    for r in costs:
        print("  ", r)
    print("Supply:", supply)
    print("Demand:", demand)
    print()

    # 2. баланс
    try:
        check_balance(supply, demand)
    except ValueError as e:
        print("ERROR:", e)
        return

    m = len(supply)
    n = len(demand)

    # 3. начальное решение (Least Cost / matrix minima)
    alloc_lc, cost_lc, steps_lc, occupied, expected = least_cost_initial(
        costs, supply, demand
    )

    print("== Least Cost method (initial BFS) ==")
    for stp in steps_lc:
        print(
            f"Step {stp['step']:>2}: "
            f"cell (S{stp['cell'][0]}, D{stp['cell'][1]}), "
            f"cost = {stp['cost']}, "
            f"allocated = {stp['allocated']}, "
            f"supply→ {stp['supply_after']}, "
            f"demand→ {stp['demand_after']}"
        )

    print("\nAllocation (LC):")
    for row in alloc_lc:
        print("  ", [int(x) if float(x).is_integer() else x for x in row])
    print(f"Total LC cost: {int(cost_lc)}")

    # 4. проверка на вырожденность
    is_degenerate = occupied < expected
    if is_degenerate:
        print(
            f"\nDegenerate BFS detected: occupied = {occupied}, "
            f"required = {expected} (= m + n - 1). Adding ε to make it basic..."
        )
        alloc_fixed, _ = fix_degeneracy(alloc_lc, occupied, expected)
    else:
        print(
            f"\nNon-degenerate BFS: occupied = {occupied} = m + n - 1 ({expected})"
        )
        alloc_fixed = alloc_lc

    # 5. MODI
    alloc_opt, cost_opt, modi_steps = modi_optimize(costs, alloc_fixed)

    print("\n== MODI optimization ==")
    if not modi_steps:
        print("All w_ij ≤ 0 → initial plan is already optimal.")
    else:
        for k, it in enumerate(modi_steps, start=1):
            print(
                f"Iter {k}: enter (S{it['entering'][0]}, D{it['entering'][1]}), "
                f"w = {it['w']:.2f}, θ = {it['theta']}, loop = {it['loop']}"
            )

    print("\nFinal allocation (after MODI):")
    for row in alloc_opt:
        # убираем .0 у целых
        printable = [int(x) if abs(x - int(x)) < 1e-9 else x for x in row]
        print("  ", printable)

    print(f"\nFinal cost: {int(cost_opt)}")


if __name__ == "__main__":
    main()