import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from scipy.optimize import milp, LinearConstraint, Bounds

# 1. Page Config
st.set_page_config(page_title="IPL Moneyball Engine", layout="wide", page_icon="🏏")

# 2. Robust Data Loading
@st.cache_data
def load_and_prep_data():
    csv_file = "cleaned_ipl_metrics_2024.csv"
    if not os.path.exists(csv_file):
        st.error(f"⚠️ Could not find `{csv_file}` in the directory. Please ensure it is uploaded to your GitHub repository.")
        st.stop()

    df = pd.read_csv(csv_file)

    df = df.rename(columns={
        "COST IN ₹ (CR.)": "Cost_Cr",
        "Total Contributions": "Total_Impact",
        "Contribution Per Crore": "Value_Score",
        "TYPE": "Role"
    })

    df = df.dropna(subset=['Cost_Cr', 'Total_Impact', 'Role', 'player_name']).copy()

    df['Role'] = df['Role'].astype(str).str.strip().str.upper()
    # Fill any gaps in secondary fields rather than dropping rows over them
    if 'Value_Score' in df.columns:
        df['Value_Score'] = df['Value_Score'].fillna(0)
    if 'Team' in df.columns:
        df['Team'] = df['Team'].fillna("Unknown")

    df['Plotly_Size'] = np.clip(df['Value_Score'], 0.1, None)

    return df

df = load_and_prep_data()

ROLE_COLORS = {
    "BATTER": "#636EFA",
    "BOWLER": "#EF553B",
    "ALL-ROUNDER": "#00CC96",
    "WICKETKEEPER": "#AB63FA"
}
# Any role value not in the map above still gets a color instead of breaking the chart
FALLBACK_PALETTE = px.colors.qualitative.Set2
unmapped_roles = [r for r in df['Role'].unique() if r not in ROLE_COLORS]
for i, r in enumerate(unmapped_roles):
    ROLE_COLORS[r] = FALLBACK_PALETTE[i % len(FALLBACK_PALETTE)]

# 3. Header
st.title("🏏 IPL Auction: Moneyball Squad Optimizer")
st.caption("Data-Driven Resource Allocation & Integer Programming for Franchise Management")
st.divider()

tab1, tab2 = st.tabs(["⚡ Squad Optimizer (ILP)", "🔍 Player Valuation & Search"])

# ==========================================
# TAB 1: INTEGER PROGRAMMING OPTIMIZER
# ==========================================
with tab1:
    st.subheader("🎯 Mathematical Squad Builder")
    st.markdown(
        "Set your total purse and minimum role counts. The algorithm solves a "
        "**0/1 Knapsack Optimization Problem** to build the highest-impact squad possible "
        "under those constraints."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        total_purse = st.number_input("Total Purse Budget (₹ Crores)", min_value=1.0, max_value=150.0, value=25.0, step=1.0)
    with col_b:
        squad_size = st.slider("Target Squad Size", min_value=3, max_value=11, value=7)

    st.markdown("**Minimum players required per role** (set 0 to leave unconstrained):")
    role_cols = st.columns(4)
    role_quota_inputs = {}
    known_roles = ["BATTER", "BOWLER", "ALL-ROUNDER", "WICKETKEEPER"]
    for i, role in enumerate(known_roles):
        with role_cols[i]:
            available = int((df['Role'] == role).sum())
            role_quota_inputs[role] = st.number_input(
                f"Min {role.title()}s", min_value=0, max_value=max(available, 0),
                value=min(1, available), step=1, key=f"quota_{role}"
            )

    quota_sum = sum(role_quota_inputs.values())
    if quota_sum > squad_size:
        st.warning(
            f"Your role minimums add up to {quota_sum}, which is more than your squad size of "
            f"{squad_size}. The optimizer will report infeasibility unless you adjust one of these."
        )

    run_clicked = st.button("🚀 Run Squad Optimizer", type="primary")

    if run_clicked:
        n = len(df)
        c = -df['Total_Impact'].values  # maximize impact == minimize negative impact
        costs = df['Cost_Cr'].values

        A_rows = [costs, np.ones(n)]
        lb = [0, squad_size]
        ub = [total_purse, squad_size]

        for role, min_count in role_quota_inputs.items():
            if min_count > 0:
                A_rows.append((df['Role'] == role).astype(int).values)
                lb.append(min_count)
                ub.append(np.inf)

        A = np.vstack(A_rows)
        constraints = LinearConstraint(A, lb=lb, ub=ub)
        integrality = np.ones(n)
        bounds = Bounds(0, 1)

        res = milp(c=c, integrality=integrality, constraints=constraints, bounds=bounds)

        if res.success:
            selected_indices = np.where(res.x > 0.5)[0]
            opt_squad = df.iloc[selected_indices].copy()
            st.session_state["opt_squad"] = opt_squad
            st.session_state["opt_purse"] = total_purse
        else:
            st.session_state["opt_squad"] = None
            st.error(
                "No valid squad could be built within these constraints. Try increasing the "
                "purse, reducing role minimums, or adjusting squad size."
            )

    # Persisted display: survives reruns triggered by other widgets (e.g. tab2 search box)
    opt_squad = st.session_state.get("opt_squad")
    if opt_squad is not None and not opt_squad.empty:
        used_purse = st.session_state.get("opt_purse", total_purse)
        used_budget = round(opt_squad['Cost_Cr'].sum(), 2)
        total_impact = round(opt_squad['Total_Impact'].sum(), 2)

        st.success(
            f"Optimized Squad: Total Spend ₹{used_budget} Cr / ₹{used_purse} Cr | "
            f"Predicted Impact: {total_impact}"
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Selected Players", len(opt_squad))
        m2.metric("Remaining Purse", f"₹{round(used_purse - used_budget, 2)} Cr")
        m3.metric("Avg Value Rating", round(opt_squad['Value_Score'].mean(), 2))

        role_breakdown = opt_squad['Role'].value_counts().to_dict()
        st.caption("Role mix: " + ", ".join(f"{k}: {v}" for k, v in role_breakdown.items()))

        st.dataframe(
            opt_squad[['player_name', 'Role', 'Cost_Cr', 'Total_Impact', 'Value_Score', 'Team']].reset_index(drop=True),
            use_container_width=True
        )

        csv_data = opt_squad.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Optimized Squad (CSV)", csv_data, "optimized_ipl_squad.csv", "text/csv")

# ==========================================
# TAB 2: EXPLORATORY VISUALS & SEARCH
# ==========================================
with tab2:
    st.subheader("📊 Individual Player Valuation & Filtering")

    min_cost = float(df['Cost_Cr'].min())
    max_cost = float(df['Cost_Cr'].max())

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search_query = st.text_input("🔍 Search Player Name", "")
    with col_f2:
        max_player_cost = st.slider(
            "Max Single Player Cost (₹ Cr)",
            min_value=min_cost, max_value=max_cost, value=max_cost
        )

    filtered = df[df['Cost_Cr'] <= max_player_cost]
    if search_query:
        filtered = filtered[filtered['player_name'].str.contains(search_query, case=False, na=False)]

    if not filtered.empty:
        fig = px.scatter(
            filtered,
            x="Cost_Cr",
            y="Total_Impact",
            color="Role",
            size="Plotly_Size",
            hover_name="player_name",
            color_discrete_map=ROLE_COLORS,
            hover_data={"Cost_Cr": True, "Total_Impact": True, "Value_Score": True, "Team": True, "Plotly_Size": False},
            labels={"Cost_Cr": "Auction Cost (Crores ₹)", "Total_Impact": "On-Field Impact Score", "Role": "Player Role"},
            template="plotly_dark",
            title="Price vs. On-Field Impact (Top-Left Quadrant = Undervalued Gems)"
        )
        fig.add_hline(y=filtered['Total_Impact'].median(), line_dash="dot", line_color="gray")
        fig.add_vline(x=filtered['Cost_Cr'].median(), line_dash="dot", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            filtered[['player_name', 'Role', 'Cost_Cr', 'Total_Impact', 'Value_Score', 'Team']].reset_index(drop=True),
            use_container_width=True
        )
    else:
        st.warning("No players match your search criteria.")
