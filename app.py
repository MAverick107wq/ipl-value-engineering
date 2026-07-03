%%writefile app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title='IPL Value Engineering Dashboard', page_icon='🏏', layout='wide')

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_ipl_metrics_2024.csv')

    for col in ['Sold Price (Rs)', 'Total Runs Scored', 'Total Wickets Taken', 'Cost Per Run', 'Cost Per Wicket', 'Contribution Per Crore']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Team' in df.columns:
        df['Team'] = df['Team'].astype(str).str.strip()

    if 'player_name' in df.columns:
        df['player_name'] = df['player_name'].astype(str).str.strip()

    return df

df = load_data()

st.title('IPL Value Engineering Dashboard')
st.markdown('Interactive analytics for auction value, player output, and franchise efficiency.')

all_teams = sorted([t for t in df['Team'].dropna().unique().tolist() if t not in ['', 'None', 'Unsold']])
selected_teams = st.sidebar.multiselect('Franchise / Team', all_teams, default=all_teams)

filtered_df = df[df['Team'].isin(selected_teams)].copy() if selected_teams else df.iloc[0:0].copy()

if filtered_df.empty:
    st.warning('No data available for the selected team filter.')
    st.stop()

team_spend = filtered_df['Sold Price (Rs)'].fillna(0).sum()
team_runs = filtered_df['Total Runs Scored'].fillna(0).sum()
team_wickets = filtered_df['Total Wickets Taken'].fillna(0).sum()
overall_cpr = team_spend / team_runs if team_runs else np.nan

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric('Total Spend', f'₹{team_spend:,.0f}')
kpi2.metric('Total Runs', f'{team_runs:,.0f}')
kpi3.metric('Total Wickets', f'{team_wickets:,.0f}')
kpi4.metric('Overall Financial Efficiency', f'₹{overall_cpr:,.2f} per run' if pd.notna(overall_cpr) else 'N/A')

st.markdown('### Player Value Scatter Plots')
plot_left, plot_right = st.columns(2)

batsmen_df = filtered_df[(filtered_df['Total Runs Scored'].fillna(0) > 0) & (filtered_df['Sold Price (Rs)'].fillna(0) > 0)].copy()

fig_bat = px.scatter(
    batsmen_df,
    x='Total Runs Scored',
    y='Sold Price (Rs)',
    color='Team',
    hover_data=['player_name', 'Total Wickets Taken', 'Cost Per Run', 'Cost Per Wicket'],
    title='Batsmen Value Map',
    labels={'Total Runs Scored': 'Total Runs Scored', 'Sold Price (Rs)': 'Sold Price (Rs)'},
    template='plotly_white'
)

fig_bat.add_annotation(
    text='Bottom-right quadrant = Hidden Gems',
    xref='paper',
    yref='paper',
    x=0.98,
    y=0.02,
    showarrow=False,
    align='right',
    font=dict(size=12, color='gray')
)

fig_bat.update_layout(height=550, legend_title_text='Franchise / Team')

bowlers_df = filtered_df[(filtered_df['Total Wickets Taken'].fillna(0) > 0) & (filtered_df['Sold Price (Rs)'].fillna(0) > 0)].copy()

fig_bowl = px.scatter(
    bowlers_df,
    x='Total Wickets Taken',
    y='Sold Price (Rs)',
    color='Team',
    hover_data=['player_name', 'Total Runs Scored', 'Cost Per Run', 'Cost Per Wicket'],
    title='Bowlers Value Map',
    labels={'Total Wickets Taken': 'Total Wickets Taken', 'Sold Price (Rs)': 'Sold Price (Rs)'},
    template='plotly_white'
)

fig_bowl.add_annotation(
    text='Bottom-right quadrant = Hidden Gems',
    xref='paper',
    yref='paper',
    x=0.98,
    y=0.02,
    showarrow=False,
    align='right',
    font=dict(size=12, color='gray')
)

fig_bowl.update_layout(height=550, legend_title_text='Franchise / Team')

plot_left.plotly_chart(fig_bat, use_container_width=True)
plot_right.plotly_chart(fig_bowl, use_container_width=True)

st.markdown('### Leaderboards')

paid_df = filtered_df.copy()
paid_df = paid_df[paid_df['Sold Price (Rs)'].fillna(0) > 0].copy()
paid_df = paid_df[~paid_df['Team'].astype(str).str.upper().isin(['UNSOLD'])].copy()

undervalued_batsmen = paid_df[(paid_df['Total Runs Scored'] >= 150) & (paid_df['Cost Per Run'].notna())].copy()
undervalued_batsmen = undervalued_batsmen.sort_values(['Cost Per Run', 'Total Runs Scored'], ascending=[True, False]).head(5)

undervalued_bowlers = paid_df[(paid_df['Total Wickets Taken'] >= 10) & (paid_df['Cost Per Wicket'].notna())].copy()
undervalued_bowlers = undervalued_bowlers.sort_values(['Cost Per Wicket', 'Total Wickets Taken'], ascending=[True, False]).head(5)

lb_left, lb_right = st.columns(2)

show_bat_cols = ['player_name', 'Team', 'Total Runs Scored', 'Sold Price (Rs)', 'Cost Per Run', 'Contribution Per Crore']
show_bowl_cols = ['player_name', 'Team', 'Total Wickets Taken', 'Sold Price (Rs)', 'Cost Per Wicket', 'Contribution Per Crore']

lb_left.dataframe(
    undervalued_batsmen[show_bat_cols].reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)

lb_right.dataframe(
    undervalued_bowlers[show_bowl_cols].reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)

st.markdown('### Notes')
st.info('Hidden Gems are players in the bottom-right quadrant of each scatter plot: low auction cost with strong on-field output.')