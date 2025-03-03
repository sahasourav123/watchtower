"""
Created On: July 2024
Created By: Sourav Saha
"""
import os
import utils
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
if os.getenv('ENV') == 'production':
    tracking_script = f"""
        <!-- Google Analytics (watchtower) -->
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

stats = backend.get_monitor_stats(user_code)

st.subheader(f"Active Monitor Count {'(Global)' if user_code == 'guest' else ''}")
placeholder = {
    'API': 0,
    'WEBSITE': 1,
    'DOMAIN': 2,
    'SSL': 3,
    'DNS': 4,
    'TCP': 5,
    'DATABASE': 6,
    'EVENT': 7,
}

rc = st.columns(len(placeholder))

for idx, stat in enumerate(stats):
    monitor_type = stat['monitor_type'].upper()
    rc[placeholder[monitor_type]].metric(label=monitor_type, value=utils.format_large_number(stat['active_monitors'], 0))


# ======================================================================
# Execution Trends
# ======================================================================
st.subheader("Monitor Checked Count (Global)")
agg_execution_stats, execution_stats_df = backend.get_execution_stats(365 * 10)

rc = st.columns(len(placeholder))
for idx, stat in enumerate(agg_execution_stats):
    monitor_type = stat['monitor_type'].upper()
    rc[placeholder[monitor_type]].metric(label=monitor_type, value=utils.format_large_number(stat['total_checks'], 0))

# plotly bar chart
import plotly.express as px
st.plotly_chart(
    px.bar(
        execution_stats_df, y='total_count', title='Check Count Trends',
        labels={'date': 'Date', 'total_count': 'Check Count'},
        height=300,
    ),
    use_container_width=True,
)
