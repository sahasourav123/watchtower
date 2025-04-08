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
user_code = auth.who_am_i()

if user_code == 'guest':
    st.warning("You are accessing this page as **Guest**. Only sample monitors are displayed")

cc = st.columns([1, 4])
day_limit = cc[0].number_input('Day Limit', value=UPTIME_HISTORY_LIMIT, min_value=1, max_value=90)

uptime_df = backend.fetch_uptime_history(user_code, day_limit)
if uptime_df.empty:
    st.info("No Response Analytics Data found.. ")
    st.page_link("pages/show-monitors.py", label=f"**Goto Monitor List**", icon=":material/lists:")
    st.stop()

response_stats_df = backend.get_daily_response_stats(user_code, day_limit)
selected_monitor_group = cc[1].multiselect('Select Monitor Group(s)', uptime_df['monitor_group'].unique())
if selected_monitor_group:
    uptime_df = uptime_df[uptime_df['monitor_group'].isin(selected_monitor_group)]
    response_stats_df = response_stats_df[response_stats_df['monitor_group'].isin(selected_monitor_group)]

filter_monitor_type = st.radio(
    'Select Monitor Type',
    sorted(uptime_df['monitor_type'].str.upper().unique()),
    horizontal=True
).lower()


# ===========================================================
# Response Time Statistics
# ===========================================================
def response_time_analytics():

    st.subheader(":material/timer: Response Time Statistics")
    # filter df for monitor type: api, website, server
    filtered_df = uptime_df[uptime_df['monitor_type'] == filter_monitor_type]
    time_unit = "s" if filter_monitor_type == "event" else "ms"

    # Box Plot for Avg Response Time
    fig4 = px.box(filtered_df, x='monitor_name', y='avg_rt', title=f'Average Response Time({time_unit}) Distribution')
    fig4.update_layout(yaxis_title=f'Average Response Time ({time_unit})', xaxis_title='Monitor Name')

    # Box Plot for P90 Response Time
    fig5 = px.box(filtered_df, x='monitor_name', y='p90_rt', title=f'90th Percentile Response Time({time_unit}) Distribution')
    fig5.update_layout(yaxis_title=f'90th Percentile Response Time ({time_unit})', xaxis_title='Monitor Name')

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
        'database': 'status',
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

    if filtered_df.empty:
        st.warning("No data available for the selected filter")
        return

    # check complete date range last n days
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    end_date = filtered_df['date'].max()
    start_date = end_date - pd.DateOffset(days=day_limit)
    full_date_range = pd.date_range(start=start_date, end=end_date)

    selected_scale = cc[1].radio('Select Scale', options=['Linear', 'Logarithmic'], index=1, horizontal=True)

    for monitor_group, monitor_df_grouped in filtered_df.groupby('monitor_group'):
        st.divider()
        st.subheader(f":blue[:material/double_arrow: {monitor_group} ({monitor_df_grouped['monitor_id'].nunique()})]")

        for monitor_id, stat_df in monitor_df_grouped.groupby('monitor_id'):
            monitor_name = stat_df['monitor_name'].iloc[-1]
            st.subheader(monitor_name)
            missing_dates = set(full_date_range) - set(stat_df['date'])
            padding_df = pd.DataFrame(missing_dates, columns=['date'])
            sized_df = pd.concat([padding_df, stat_df]).set_index('date').sort_index()
            sized_df = sized_df.fillna({'response': 0, 'total': 0})

            if response_type_map[filter_monitor_type] == 'status':
                fig = px.bar(
                    sized_df, x=sized_df.index, y="total", color="response",
                    color_discrete_map={
                        '0': 'dodgerblue',
                        '200': 'dodgerblue',
                        '404': 'brown',
                        '500': 'red'
                    },
                    category_orders={
                        'response': sorted(sized_df['response'].astype(int).unique())
                    },
                    log_y=True if selected_scale == 'Logarithmic' else False,
                )

            else:
                fig = px.bar(
                    sized_df, x=sized_df.index, y="response",
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
