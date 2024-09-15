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

monitor_df = backend.fetch_monitors({'user_code': user_code})

if monitor_df.empty:
    st.warning("No monitors created yet.")
    st.stop()

def _display_monitor(monitor):
    st.subheader(f"{'🟢' if monitor['is_active'] else '🔴'} [{monitor['monitor_type'].upper()}] {monitor['monitor_name']}")
    cc = st.columns([1, 2, 1])
    with cc[0]:
        # st.subheader(f"{'🟢' if monitor['is_active'] else '🔴'} {monitor['monitor_name']}")
        st.markdown(f"""
        | ID | #{monitor['monitor_id']} |
        |----|---|
        | Interval (sec) | {monitor['interval']} |
        | Timeout (sec) | {monitor['timeout']} |
        | Created On | {parser.parse(monitor['created_at']).strftime('%Y-%m-%d')}
        """)

    with cc[1]:
        st.write(f"Monitor Config")
        _config = yaml.safe_dump(monitor['monitor_body'], default_flow_style=False)
        st.code(_config, language='yaml')

    with cc[2]:
        st.write("Expectation")
        _expect = yaml.safe_dump(monitor['expectation'], default_flow_style=False)
        st.code(_expect, language='yaml')
    pass


for index, row in monitor_df.iterrows():
    _display_monitor(row)
    st.divider()

