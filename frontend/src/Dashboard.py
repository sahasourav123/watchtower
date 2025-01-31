"""
Created On: July 2024
Created By: Sourav Saha
"""
from utils import logger
import streamlit as st
from svc import svc_backend as backend
from __version__ import __version__

# ======================================================================
# Start Application
# ======================================================================
st.set_page_config(layout='wide', page_title='The Watchtower', initial_sidebar_state='expanded')
st.image('assets/watchtower.jpeg')
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

# ======================================================================
import auth
user_code = auth.ensure_logged_in('guest')

if user_code:
    stats = backend.get_stats(user_code)
    st.dataframe(stats, column_config={'monitor_type': 'Type', 'total_monitors': 'Total', 'active_monitors': 'Active'})
