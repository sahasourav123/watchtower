"""
Created On: Feb 2025
Created By: Sourav Saha
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from svc import svc_backend as backend
from constants import UPTIME_HISTORY_LIMIT


st.set_page_config(layout='wide', page_title='Response Analytics', initial_sidebar_state='expanded')
st.header("Response Analytics")

import auth
user_code = auth.ensure_logged_in()

if user_code == 'guest':
    st.warning("You are accessing this page as **Guest**. Only sample monitors are displayed")

cc = st.columns([1, 4])
day_limit = cc[0].number_input('Day Limit', value=UPTIME_HISTORY_LIMIT, min_value=1, max_value=90)

uptime_df = backend.fetch_uptime_history(user_code, day_limit)
response_stats_df = backend.get_daily_response_stats(user_code)
filter_monitor_type = cc[1].radio('Select Monitor Type', sorted(uptime_df['monitor_type'].unique()), horizontal=True)


# ===========================================================
# Response Time Statistics
# ===========================================================
def response_time_analytics():

    st.subheader(":material/timer: Response Time Statistics")
    # filter df for monitor type: api, website, server
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


# ===========================================================
# Response Code Statistics
# ===========================================================
def response_code_analytics():
    st.subheader(":material/123: Response Trends")
    response_stats_df['response'] = response_stats_df['response'].astype(str)
    response_type_map = {
        'api': 'status',
        'website': 'status',
        'dns': 'status',
        'tcp': 'status',
        'ssl': 'count',
        'domain': 'count',
        'event': 'count',
    }

    cc = st.columns(2)
    # Apply Filter
    filter_outcome = cc[0].radio('Response Outcome', options=['All', 'Success', 'Failure'], index=0, horizontal=True)
    if filter_outcome == 'Success':
        outcome_flag = [True]
    elif filter_outcome == 'Failure':
        outcome_flag = [False]
    else:
        outcome_flag = [True, False]

    filtered_df = response_stats_df[(response_stats_df['monitor_type'] == filter_monitor_type) & (response_stats_df['is_success'].isin(outcome_flag))]
    with st.expander("Show Response Stats"):
        _column_config = {
            'date': st.column_config.DateColumn('Date'),
            'monitor_group': 'Group',
            'monitor_name': 'Monitor Name',
            'monitor_id': 'ID #',
            'is_success': 'Is Success',
            'response': 'Response',
            'total': 'Count',
            'last_check_time': st.column_config.DatetimeColumn('Last Check', timezone='Asia/Kolkata'),
        }
        st.dataframe(filtered_df, column_config=_column_config, column_order=_column_config.keys(), hide_index=True)

    if filtered_df.empty:
        st.warning("No data available for the selected filter")
        return

    selected_scale = cc[1].radio('Select Scale', options=['Linear', 'Logarithmic'], index=1, horizontal=True)
    for monitor_id, stat_df in filtered_df.groupby('monitor_id'):
        monitor_name = stat_df['monitor_name'].iloc[-1]

        if response_type_map[filter_monitor_type] == 'status':
            fig = px.bar(
                stat_df, x="date", y="total", color="response", color_discrete_map={'0': 'green', '200': 'green', '404': 'brown', '500': 'red'},
                category_orders={'response': sorted(stat_df['response'].unique())},
                log_y=True if selected_scale == 'Logarithmic' else False,
            )

        else:
            fig = px.bar(
                stat_df, x="date", y="response",
                log_y=True if selected_scale == 'Logarithmic' else False,
            )

        fig.update_layout(
            title=f"{monitor_name} (#{monitor_id})",
            height=220,
            xaxis={'title': 'Date'},
            yaxis={'title': None},
        )
        st.plotly_chart(fig)


# ===========================================================
# Display Tabs
# ===========================================================
analytics_tabs = st.tabs([":material/123: Response Trends", ":material/timer: Response Time"])

with analytics_tabs[0]:
    response_code_analytics()

with analytics_tabs[1]:
    response_time_analytics()
