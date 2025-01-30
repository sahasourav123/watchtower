import pandas as pd
import plotly.express as px
import streamlit as st
from svc import svc_backend as backend

st.header("Uptime History")

import auth
user_code = auth.ensure_logged_in(required_access_level='viewer')

day_limit = st.number_input('Day Limit', value=60, min_value=1, max_value=90)
df = backend.fetch_uptime_history(user_code, day_limit)

# st.dataframe(df, hide_index=True)

df['date'] = pd.to_datetime(df['date'])

# Function to determine bar color based on uptime
def get_bar_color(uptime_pct):
    if uptime_pct < 90.0:
        return 'red'
    elif uptime_pct < 100:
        return 'orange'
    else:
        return 'green'


import plotly.graph_objects as go

for monitor_name in df['monitor_name'].unique():
    df_monitor = df[df['monitor_name'] == monitor_name]

    fig = go.Figure()

    for index, row in df_monitor.iterrows():
        bar_color = get_bar_color(row['uptime_pct'])

        fig.add_trace(go.Bar(
            x=[row['date']],
            y=[1],
            marker_color=bar_color,
            hoverinfo='text',
            hovertext=f"Date: {row['date'].strftime('%Y-%m-%d')}<br>Uptime: {row['uptime_pct']}%"
        ))

    fig.update_layout(
        title=monitor_name,
        xaxis=dict(
            # title='Date',
            tickvals=df_monitor['date'],
            tickformat='%d %b'
        ),
        yaxis=dict(
            # title='Uptime',
            showticklabels=False
        ),
        showlegend=False,
        height=140,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    st.plotly_chart(fig)

# Box Plot for Avg Response Time
fig4 = px.box(df, x='monitor_name', y='avg_rt', title='Average Response Time Distribution')
fig4.update_layout(yaxis_title='Average Response Time (ms)')

# Box Plot for P90 Response Time
fig5 = px.box(df, x='monitor_name', y='p90_rt', title='90th Percentile Response Time Distribution')
fig5.update_layout(yaxis_title='90th Percentile Response Time (ms)')

# Show the figures
st.plotly_chart(fig4)
st.plotly_chart(fig5)