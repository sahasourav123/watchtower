import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from svc import svc_backend as backend
from constants import UPTIME_HISTORY_LIMIT

st.set_page_config(layout='wide', page_title='Uptime History', initial_sidebar_state='expanded')
st.header("Uptime History")

import auth
user_code = auth.who_am_i()

if user_code == 'guest':
    st.warning("You are accessing this page as **Guest**. Only sample monitors are displayed")

cc = st.columns([1, 4])
day_limit = cc[0].number_input('Day Limit', value=UPTIME_HISTORY_LIMIT, min_value=1, max_value=90)
uptime_df = backend.fetch_uptime_history(user_code, day_limit)
selected_monitor_group = cc[1].multiselect('Select Monitor Group(s)', uptime_df['monitor_group'].unique())

# display selected groups in red
if selected_monitor_group:
    uptime_df = uptime_df[uptime_df['monitor_group'].isin(selected_monitor_group)]

uptime_df['date'] = pd.to_datetime(uptime_df['date'])

# check complete date range last n days
start_date = uptime_df['date'].max() - pd.DateOffset(days=day_limit)
full_date_range = pd.date_range(start=start_date, end=uptime_df['date'].max())

# Function to determine bar color based on uptime
def get_bar_color(uptime_pct):
    if uptime_pct < 0:
        return 'white'
    elif uptime_pct < 90.0:
        return 'red'
    elif uptime_pct < 100:
        return 'orange'
    else:
        return 'green'


# Plot Uptime History
for monitor_group, monitor_df_grouped in uptime_df.groupby('monitor_group'):
    st.divider()
    st.subheader(f":blue[:material/double_arrow: {monitor_group} ({monitor_df_grouped['monitor_id'].nunique()})]")

    for monitor_id, df_monitor in monitor_df_grouped.groupby('monitor_id'):

        # Calculate Mean Uptime
        avg_uptime = df_monitor['uptime_pct'].mean()
        monitor_name = df_monitor['monitor_name'].iloc[-1]
        monitor_type = df_monitor['monitor_type'].iloc[-1]

        fig = go.Figure()
        sized_df = df_monitor.set_index('date').reindex(full_date_range).fillna({'uptime_pct': -1})

        # create color bar indicating uptime pct
        for _date, row in sized_df.iterrows():
            bar_color = get_bar_color(row['uptime_pct'])

            fig.add_trace(go.Bar(
                x=[_date],
                y=[1],
                marker_color=bar_color,
                hoverinfo='text',
                hovertext=f"Date: {_date.strftime('%Y-%m-%d')}<br>Uptime: {row['uptime_pct']}%"
            ))

        fig.update_layout(
            title=f"{monitor_type} | {monitor_name} (#{monitor_id})",
            xaxis=dict(
                # title='Date',
                tickvals=full_date_range[::max(1, len(full_date_range)//10)],
                tickformat='%d %b'
            ),
            yaxis=dict(
                # title='Uptime',
                showticklabels=False
            ),
            showlegend=False,
            height=120,
            margin=dict(l=0, r=0, t=30, b=0)
        )

        cc = st.columns([6, 1])
        cc[0].plotly_chart(fig)
        cc[1].metric('Mean Uptime', f"{avg_uptime:.1f}%")
