"""
Created On: July 2024
Created By: Sourav Saha
"""
import utils
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

monitor_df = backend.fetch_monitors(1)
st.dataframe(monitor_df)
