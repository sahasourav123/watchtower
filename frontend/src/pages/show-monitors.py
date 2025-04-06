import yaml
import streamlit as st
from svc import svc_backend as backend
from constants import OUTCOME_HISTORY_LIMIT, PUSH_EVENT_ENDPOINT

import auth

st.set_page_config(layout='wide', page_title='Show Monitors', initial_sidebar_state='expanded')
user_code = auth.who_am_i()

st.header("Manage Monitors")

def _display_monitor(monitor):
    monitor_id = monitor['monitor_id']
    _tags = ', '.join([f"`{tag}`" for tag in monitor.get('tags')]) if monitor['tags'] else '`-`'
    title = f"**[{monitor['monitor_type'].upper()}] {monitor['monitor_name']}**"
    st.write(title)

    cc = st.columns([2, 1])
    with cc[0]:
        # Edit Monitor Name
        _name = st.text_input("Edit Monitor Name", value=monitor['monitor_name'])
        if _name != monitor['monitor_name']:
            res = backend.update_monitor(user_code, monitor_id, {'monitor_name': _name})
            st.toast("Monitor Name updated successfully", icon='🟢')

    with cc[1]:
        # Edit Monitor Group
        _group = st.text_input("Edit Monitor Group", value=monitor['monitor_group'])
        if _group != monitor['monitor_group']:
            res = backend.update_monitor(user_code, monitor_id, {'monitor_group': _group})
            st.toast("Monitor Group updated successfully", icon='🟢')

    cc = st.columns([1, 2, 1])
    with cc[0]:
        # Edit Check Interval
        _interval = st.text_input(f"Edit Check Interval ({monitor['interval_unit']})", value=monitor['interval'])
        if _interval != monitor['interval']:
            res = backend.update_monitor(user_code, monitor_id, {'interval': _interval})
            st.toast("Monitor Interval updated successfully", icon='🟢')

        # Edit Timeout
        _timeout = st.text_input("Edit Timeout (sec)", value=monitor['timeout'])
        if int(_timeout) != monitor['timeout']:
            res = backend.update_monitor(user_code, monitor_id, {'timeout': _timeout})
            st.toast(f"Monitor Timeout updated successfully", icon='🟢')

    with cc[1]:
        st.write(f"Monitor Config (read-only)")
        _config = yaml.safe_dump(monitor['monitor_body'], default_flow_style=False)
        st.code(_config, language='yaml')

    with cc[2]:
        st.write("Expectation (read-only)")
        _expect = yaml.safe_dump(monitor['expectation'], default_flow_style=False) if monitor['expectation'] else "<AUTO>"
        st.code(_expect, language='yaml')

    # Display Event Push URL for the selected monitor
    monitor_hash = monitor['monitor_body'].get('hash')
    if monitor_hash:
        st.markdown("**Push Event URL**")
        st.code(f"{PUSH_EVENT_ENDPOINT}?monitor_id={monitor_id}&hash={monitor_hash}&outcome=true&response=0&response_time=0",
                language='http', wrap_lines=True)

    cc = st.columns([1, 1, 1, 3])

    if cc[0].button(":material/bolt: Run Monitor"):
        res = backend.run_monitor(user_code, monitor_id)
        st.json(res)

    if cc[1].button(":material/play_pause: Pause / Resume"):
        res = backend.update_monitor(user_code, monitor_id, {'is_active': not monitor['is_active']})
        if res['status'] == 'success':
            _updated_state = 'Paused' if monitor['is_active'] else 'Resumed'
            st.rerun()
        else:
            st.error("Failed to pause monitor. Please try again later")

    if cc[2].button(":material/delete: Delete Monitor", type='primary'):
        res = backend.delete_monitor(user_code, monitor_id)
        if res['status'] == 'success':
            st.rerun()
        else:
            st.error("Failed to delete monitor. Please try again later")
    pass


if user_code == 'guest':
    st.warning("You are accessing this page as **Guest**. Only sample monitors are displayed")

@st.cache_data(ttl=60)
def get_monitors():
    # fetch monitors & run history
    _monitor_df = backend.fetch_monitors(user_code)
    _monito_history_df = backend.fetch_monitor_history(user_code, OUTCOME_HISTORY_LIMIT)

    # merge monitor and history
    _monitor_df = _monitor_df.merge(_monito_history_df, on='monitor_id', how='left')

    def concat_interval(row):
        return f"{row['interval']} {row['interval_unit']}" if row['interval_unit'] != 'cron' else row['interval']

    _monitor_df['display_interval'] = _monitor_df.apply(concat_interval, axis=1)
    return _monitor_df


monitor_df = get_monitors()
selected_monitor_group = st.multiselect('Select Monitor Group(s)', monitor_df['monitor_group'].unique())
if selected_monitor_group:
    monitor_df = monitor_df[monitor_df['monitor_group'].isin(selected_monitor_group)]
st.subheader(f"Monitor List ({monitor_df.shape[0]})")

if monitor_df.empty:
    st.warning("No monitors created yet.")
    st.stop()

# display monitors
column_config = {
    'monitor_id': 'ID #',
    'monitor_group': 'Group',
    'monitor_name': 'Monitor Name',
    'monitor_type': st.column_config.ListColumn("Type"),
    'is_active': 'Is Active',
    'display_interval': 'Check Interval',
    'outcomes': st.column_config.BarChartColumn('Recent Outcomes', width='medium', help=f'Last {OUTCOME_HISTORY_LIMIT} Uptime Check Status'),
    'response_times': st.column_config.AreaChartColumn('Latency', width='medium', help=f'Last {OUTCOME_HISTORY_LIMIT} Request Latency'),
    'timeout': 'Timeout (Sec)',
    'expiry': 'Expiry Date',
    'tags': 'Tags',
    'created_at': st.column_config.DateColumn('Created On'),
}
selected_row = st.dataframe(monitor_df, hide_index=True, column_config=column_config, column_order=column_config.keys(), selection_mode=["single-row"], on_select='rerun')
selected_row_index = selected_row['selection']['rows'][0] if selected_row['selection']['rows'] else None
selected_monitor = monitor_df.iloc[selected_row_index or 0]

st.divider()
st.subheader('View & Edit Selected Monitor')

if user_code == 'guest':
    st.warning("You are accessing this page as **Guest**. You cannot edit monitors")
    st.stop()
if selected_row_index is None:
    st.info(f"Please select a row in table above to proceed >> Defaulting to first Row...")

_display_monitor(selected_monitor)
