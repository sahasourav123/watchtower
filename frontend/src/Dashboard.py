"""
Created On: July 2024
Created By: Sourav Saha
"""
import os
from utils import logger
import streamlit as st
from svc import svc_backend as backend
from __version__ import __version__

# ======================================================================
# Start Application
# ======================================================================
st.set_page_config(layout='wide', page_title='The Watchtower', initial_sidebar_state='expanded')
with st.container(height=300, border=False):
    st.image('assets/watchtower.jpeg', use_column_width=True)

st.title(f'The Watchtower')
logger.info("initializing app")
svc = backend.load_service()
st.write(f"*Frontend: {__version__} | Backend: {svc['version']}*")

style = """
div.stButton button {
    width: 150px;
}
"""
st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

# ======================================================================
# Google Analytics Tracking
# ======================================================================
env = os.getenv('ENV', 'development')
if env == 'production':
    tracking_script = f"""
        <!-- Google Analytics (screener-web) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={os.getenv('GTAG')}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
        
          gtag('config', '{os.getenv('GTAG')}');
        </script>
        """

    html = os.path.dirname(st.__file__)+'/static/index.html'
    with open(html, 'r') as f:
        data = f.read()
        if 'Google Analytics' not in data:
            with open(html, 'w') as ff:
                modified_html = data.replace('<head>', f"<head> \n {tracking_script}")
                ff.write(modified_html)

# ======================================================================
import auth
user_code = auth.ensure_logged_in('guest')

stats = backend.get_stats(user_code)

st.subheader(f"Active Monitor Count {'(Global)' if user_code == 'guest' else ''}")
placeholder = {
    'API': 0,
    'WEBSITE': 1,
    'DOMAIN': 2,
    'SSL': 3,
    'DNS': 4,
    'TCP': 5,
    'DATABASE': 6,
}

rc = st.columns(7)

for idx, stat in enumerate(stats):
    monitor_type = stat['monitor_type'].upper()
    rc[placeholder[monitor_type]].metric(label=monitor_type, value=stat['active_monitors'])
