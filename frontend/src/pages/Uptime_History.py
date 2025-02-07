import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from svc import svc_backend as backend

st.header("Uptime History")

import auth
user_code = auth.ensure_logged_in()

if user_code == 'guest':
    st.warning("You are accessing this page as **Guest**. Only sample monitors are displayed")

day_limit = st.number_input('Day Limit', value=60, min_value=1, max_value=90)
uptime_df = backend.fetch_uptime_history(user_code, day_limit)

uptime_df['date'] = pd.to_datetime(uptime_df['date'])

# check complete date range
full_date_range = pd.date_range(start=uptime_df['date'].min(), end=uptime_df['date'].max())

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


for monitor_id, df_monitor in uptime_df.groupby('monitor_id'):
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
        title=f"{monitor_type} | {monitor_name}",
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

st.divider()
st.subheader("Response Time Statistics")
# filter df for monitor type: api, website, server
filter_monitor_type = st.radio('Select Monitor Type', sorted(uptime_df['monitor_type'].unique()), horizontal=True)
filtered_df = uptime_df[uptime_df['monitor_type'] == filter_monitor_type]

# Box Plot for Avg Response Time
fig4 = px.box(filtered_df, x='monitor_name', y='avg_rt', title='Average Response Time Distribution')
fig4.update_layout(yaxis_title='Average Response Time (ms)', xaxis_title='Monitor Name')

# Box Plot for P90 Response Time
fig5 = px.box(filtered_df, x='monitor_name', y='p90_rt', title='90th Percentile Response Time Distribution')
fig5.update_layout(yaxis_title='90th Percentile Response Time (ms)', xaxis_title='Monitor Name')

# Show the figures
st.plotly_chart(fig4)
st.plotly_chart(fig5)
