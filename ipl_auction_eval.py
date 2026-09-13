"""
IPL Auction: Moneyball Squad Optimizer -- stats script
--------------------------------------------------------
Computes:
  1. Dataset size (number of players considered)
  2. ROI % of your optimized squad vs. a naive baseline squad

Fill in the two paths / column names marked TODO, then run:
    python ipl_auction_eval.py
"""

import pandas as pd

DATA_PATH = "cleaned_ipl_metrics_2024.csv"

# TODO: set these to match your actual column names
PRICE_COL = "price_crore"       # cost of the player in Crore
IMPACT_COL = "impact_score"     # your "On-Field Impact per Crore" numerator
BUDGET = 100.0                  # total budget cap used by your optimizer (Crore)
SQUAD_SIZE = 11

# TODO: paste in the player names your ILP optimizer actually selected
OPTIMIZED_SQUAD = [
    "Player A", "Player B", "Player C",  # ...
]


def dataset_size(df: pd.DataFrame) -> int:
    return len(df)


def baseline_squad(df: pd.DataFrame, budget: float, squad_size: int) -> pd.DataFrame:
    """Naive baseline: greedily pick the highest-impact players you can
    still afford, one at a time, until the squad is full or budget runs out.
    This mimics what a human might do without optimization."""
    remaining_budget = budget
    picks = []
    for _, row in df.sort_values(IMPACT_COL, ascending=False).iterrows():
        if len(picks) >= squad_size:
            break
        if row[PRICE_COL] <= remaining_budget:
            picks.append(row)
            remaining_budget -= row[PRICE_COL]
    return pd.DataFrame(picks)


def squad_impact(df: pd.DataFrame, names: list[str]) -> float:
    return df[df["player_name"].isin(names)][IMPACT_COL].sum()


def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Dataset size: {dataset_size(df)} players")

    optimized_impact = squad_impact(df, OPTIMIZED_SQUAD)

    baseline = baseline_squad(df, BUDGET, SQUAD_SIZE)
    baseline_impact_total = baseline[IMPACT_COL].sum()

    roi_pct = (optimized_impact - baseline_impact_total) / baseline_impact_total * 100

    print(f"Optimized squad total impact: {optimized_impact:.2f}")
    print(f"Baseline squad total impact:  {baseline_impact_total:.2f}")
    print(f"ROI improvement vs. baseline: {roi_pct:.1f}%")


if __name__ == "__main__":
    main()
