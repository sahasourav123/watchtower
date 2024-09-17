"""
Created On: July 2024
Created By: Sourav Saha
"""
import yaml
from dateutil import parser
from utils import logger
import streamlit as st
from svc import svc_backend as backend
from __version__ import __version__

# ======================================================================
# Start Application
# ======================================================================
st.set_page_config(layout='wide', page_title='The Watchtower', initial_sidebar_state='expanded')
st.title(f'The Watchtower')
logger.info("initializing app")
svc = backend.load_service()
st.subheader(f"*Frontend: {__version__} | Backend: {svc['version']}*")

style = """
div.stButton button {
    width: 150px;
}
"""
st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

import auth
user_code = auth.ensure_logged_in()


def _display_monitor(monitor):
    _tags = ', '.join([f"`{tag}`" for tag in monitor.get('tags')]) if monitor['tags'] else '`-`'
    _header = f"**{monitor['is_active']} [{monitor['monitor_type'].upper()}] {monitor['monitor_name']}** | _Tags:_ {_tags} | Last 20 Checks: {monitor['outcomes']}"
    with st.expander(_header):
        cc = st.columns([1, 2, 1])
        with cc[0]:
            st.text_input("Check Interval (sec)", value=monitor['interval'], key=f"{monitor['monitor_id']}_interval")
            st.text_input("Timeout (sec)", value=monitor['timeout'], key=f"{monitor['monitor_id']}_timeout")

        with cc[1]:
            st.write(f"Monitor Config")
            _config = yaml.safe_dump(monitor['monitor_body'], default_flow_style=False)
            st.code(_config, language='yaml')

        with cc[2]:
            st.write("Expectation")
            _expect = yaml.safe_dump(monitor['expectation'], default_flow_style=False)
            st.code(_expect, language='yaml')
        pass


# fetch monitors
monitor_df = backend.fetch_monitors({'user_code': user_code})
if monitor_df.empty:
    st.warning("No monitors created yet.")
    st.stop()

# fetch monitor run history
monito_history_df = backend.fetch_monitor_history({'user_code': user_code, 'limit': 20})

# merge monitor and history
monitor_df = monitor_df.merge(monito_history_df, on='monitor_id', how='left')
# replace true/false with icons
monitor_df['is_active'] = monitor_df['is_active'].apply(lambda x: '`active`' if x else '`paused`')
monitor_df['outcomes'] = monitor_df['outcomes'].str.replace('true', '🟢').str.replace('false', '🔴')

for index, row in monitor_df.iterrows():
    _display_monitor(row)

