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
st.title(f'The Watchtower')
st.markdown(f'*{__version__}*')

logger.info("initializing app")
style = """
div.stButton button {
    width: 150px;
}
"""
st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

st.json(backend.load_service())
