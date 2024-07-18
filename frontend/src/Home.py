"""
Created On: July 2024
Created By: Sourav Saha
"""
from utils import logger
import streamlit as st
from svc import svc_backend as backend

__version__ = '0.0.1'

# ======================================================================
# Start Application
# ======================================================================
st.set_page_config(layout='wide', page_title='TowerHouse', initial_sidebar_state='expanded')
st.title(f'Tower House')
st.markdown(f'*{__version__}*')

logger.info("initializing app")
style = """
div.stButton button {
    width: 150px;
}
"""
st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

st.json(backend.load_service())
