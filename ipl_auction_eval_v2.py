"""
IPL Auction: Moneyball Squad Optimizer -- stats script
--------------------------------------------------------
Matched to: cleaned_ipl_metrics_2024.csv

Computes:
  1. Dataset size (number of players considered)
  2. An optimized 11-player squad via 0/1 knapsack ILP (PuLP), maximizing
     total on-field contribution under a budget cap + role quotas
  3. A naive baseline squad (greedy, highest value-per-crore first)
  4. ROI % of the optimized squad vs. the baseline

Install once if needed:  pip install pulp --break-system-packages

Run:
    python ipl_auction_eval.py
"""

import pandas as pd
import pulp

DATA_PATH = "cleaned_ipl_metrics_2024.csv"

PRICE_COL = "COST IN ₹ (CR.)"          # player cost in Crore
IMPACT_COL = "Total Contributions"      # raw on-field impact (runs+wickets based)
VALUE_COL = "Contribution Per Crore"    # impact per crore -- used for baseline ranking
TYPE_COL = "TYPE"
NAME_COL = "player_name"

BUDGET_CR = 20.0     # TODO: set to your actual budget cap used in the ILP model
SQUAD_SIZE = 11

# TODO: set role quotas to match your original constraints (must sum <= SQUAD_SIZE)
ROLE_QUOTAS = {
    "BATTER": 3,
    "BOWLER": 3,
    "ALL-ROUNDER": 3,
    "WICKETKEEPER": 1,
}


def dataset_size(df: pd.DataFrame) -> int:
    return len(df)


def optimize_squad_ilp(df: pd.DataFrame) -> pd.DataFrame:
    """0/1 knapsack: maximize total impact subject to budget + role quotas."""
    prob = pulp.LpProblem("Squad_Optimizer", pulp.LpMaximize)
    x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in df.index}

    # Objective: maximize total on-field contribution
    prob += pulp.lpSum(x[i] * df.loc[i, IMPACT_COL] for i in df.index)

    # Budget constraint
    prob += pulp.lpSum(x[i] * df.loc[i, PRICE_COL] for i in df.index) <= BUDGET_CR

    # Total squad size (>= minimum quotas, exactly SQUAD_SIZE if enough players)
    prob += pulp.lpSum(x[i] for i in df.index) == SQUAD_SIZE

    # Role quotas (at least this many of each role)
    for role, quota in ROLE_QUOTAS.items():
        role_idx = df.index[df[TYPE_COL] == role]
        prob += pulp.lpSum(x[i] for i in role_idx) >= quota

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[prob.status] != "Optimal":
        raise RuntimeError(f"Solver status: {pulp.LpStatus[prob.status]} -- "
                            f"try relaxing BUDGET_CR or ROLE_QUOTAS")

    selected = [i for i in df.index if x[i].value() == 1]
    return df.loc[selected]


def baseline_squad(df: pd.DataFrame, budget: float, squad_size: int) -> pd.DataFrame:
    """Naive baseline: greedily pick the best value-per-crore players
    one at a time until the squad is full or budget runs out. Mimics
    what a human might do without optimization."""
    remaining_budget = budget
    picks = []
    for _, row in df.sort_values(VALUE_COL, ascending=False).iterrows():
        if len(picks) >= squad_size:
            break
        if row[PRICE_COL] <= remaining_budget:
            picks.append(row)
            remaining_budget -= row[PRICE_COL]
    return pd.DataFrame(picks)


def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Dataset size: {dataset_size(df)} players")

    optimized = optimize_squad_ilp(df)
    baseline = baseline_squad(df, BUDGET_CR, SQUAD_SIZE)

    optimized_impact = optimized[IMPACT_COL].sum()
    baseline_impact = baseline[IMPACT_COL].sum()
    optimized_cost = optimized[PRICE_COL].sum()
    baseline_cost = baseline[PRICE_COL].sum()

    roi_pct = (optimized_impact - baseline_impact) / baseline_impact * 100

    print("\nOptimized squad (ILP):")
    print(optimized[[NAME_COL, TYPE_COL, PRICE_COL, IMPACT_COL]].to_string(index=False))
    print(f"  Total cost:   {optimized_cost:.2f} Cr")
    print(f"  Total impact: {optimized_impact:.1f}")

    print("\nBaseline squad (greedy, highest value/crore first):")
    print(baseline[[NAME_COL, TYPE_COL, PRICE_COL, IMPACT_COL]].to_string(index=False))
    print(f"  Total cost:   {baseline_cost:.2f} Cr")
    print(f"  Total impact: {baseline_impact:.1f}")

    print(f"\nROI improvement vs. baseline: {roi_pct:.1f}%")


if __name__ == "__main__":
    main()
