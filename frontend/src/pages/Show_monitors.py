import yaml
import streamlit as st
from svc import svc_backend as backend

import auth

st.set_page_config(layout='wide')
user_code = auth.ensure_logged_in()

st.header("Manage Monitors")

def _display_monitor(monitor):
    _tags = ', '.join([f"`{tag}`" for tag in monitor.get('tags')]) if monitor['tags'] else '`-`'
    title = f"**[{monitor['monitor_type'].upper()}] {monitor['monitor_name']}**"
    st.write(title)
    cc = st.columns([1, 2, 1])
    with cc[0]:
        _interval = st.text_input(f"Check Interval ({monitor['interval_unit']})", value=monitor['interval'])
        if int(_interval) != monitor['interval']:
            res = backend.update_monitor(user_code, monitor['monitor_id'], {'interval': int(_interval)})
            st.toast("Monitor Interval updated successfully", icon='🟢')

        _timeout = st.text_input("Timeout (sec)", value=monitor['timeout'])
        if int(_timeout) != monitor['timeout']:
            res = backend.update_monitor(user_code, monitor['monitor_id'], {'timeout': int(_timeout)})
            st.toast(f"Monitor Timeout updated successfully", icon='🟢')

    with cc[1]:
        st.write(f"Monitor Config")
        _config = yaml.safe_dump(monitor['monitor_body'], default_flow_style=False)
        st.code(_config, language='yaml')

    with cc[2]:
        st.write("Expectation")
        _expect = yaml.safe_dump(monitor['expectation'], default_flow_style=False)
        st.code(_expect, language='yaml')

    cc = st.columns([1, 1, 4])

    if cc[0].button("Pause / Resume"):
        res = backend.update_monitor(user_code, monitor['monitor_id'], {'is_active': not monitor['is_active']})
        if res['status'] == 'success':
            _updated_state = 'Paused' if monitor['is_active'] else 'Resumed'
            st.success(f"Monitor {_updated_state} Successfully")
        else:
            st.error("Failed to pause monitor. Please try again later")

    if cc[1].button("Delete Monitor", type='primary'):
        res = backend.delete_monitor(user_code, monitor['monitor_id'])
        if res['status'] == 'success':
            st.success("Monitor Deleted Successfully")
        else:
            st.error("Failed to delete monitor. Please try again later")
    pass


if user_code == 'guest':
    st.warning("You are accessing this page as **Guest**. Only sample monitors are displayed")

# fetch monitors
monitor_df = backend.fetch_monitors(user_code)
if monitor_df.empty:
    st.warning("No monitors created yet.")
    st.stop()

# fetch monitor run history
RECENT_HISTORY_LIMIT = 25
monito_history_df = backend.fetch_monitor_history(user_code, RECENT_HISTORY_LIMIT)

# merge monitor and history
monitor_df = monitor_df.merge(monito_history_df, on='monitor_id', how='left')
monitor_df['display_interval'] = monitor_df['interval'].astype(str) + ' ' + monitor_df['interval_unit']

# display monitors
column_config = {
    'monitor_id': 'ID #',
    'monitor_name': 'Monitor Name',
    'monitor_type': st.column_config.ListColumn("Type"),
    'is_active': 'Is Active',
    'display_interval': 'Check Interval',
    'outcomes': st.column_config.BarChartColumn('Recent Outcomes', width='medium', help=f'Last {RECENT_HISTORY_LIMIT} Uptime Check Status'),
    'response_times': st.column_config.AreaChartColumn('Latency', width='medium', help=f'Last {RECENT_HISTORY_LIMIT} Request Latency'),
    'timeout': 'Timeout (Sec)',
    'created_at': st.column_config.DateColumn('Created On'),
    'expiry': 'Expiry Date',
}
selected_row = st.dataframe(monitor_df, hide_index=True, column_config=column_config, column_order=column_config.keys(), selection_mode=["single-row"], on_select='rerun')
selected_row_index = selected_row['selection']['rows'][0] if selected_row['selection']['rows'] else None
selected_monitor = monitor_df.iloc[selected_row_index or 0]

st.divider()
st.subheader('Edit Selected Monitor')

if user_code == 'guest':
    st.warning("You are accessing this page as **Guest**. You cannot edit monitors")
    st.stop()
if selected_row_index is None:
    st.info(f"Please select a row in table above to proceed >> Defaulting to first Row...")

_display_monitor(selected_monitor)
