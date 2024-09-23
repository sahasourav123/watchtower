"""
Created on: 23 Sep 2024
@author: SouravS
"""
import streamlit as st
import auth
import logging

from svc import svc_backend as backend

logger = logging.getLogger()
st.set_page_config(layout='wide')

st.header("Alert Groups")
user_code = auth.ensure_logged_in(required_access_level='viewer')

_channel_column_config = {
    'channel_name': 'Name',
    'is_active': 'status',
    'channel_type': 'Type',
    'recipient': 'Recipient',
    'remarks': 'Remarks',
}

# =================================================
# ALERTS
# =================================================
# @error_handler
def create_alert_channel():
    st.markdown("**Create Channel**")
    channel_name = st.text_input('Channel Name', placeholder='e.g. My Email Channel')
    channel_type = st.selectbox('Channel Type', options=['email', 'telegram', 'webhook'], index=0)
    recipient = st.text_input('Destination', placeholder='e.g. foo.bar@example.com')
    remarks = st.text_input('Remarks')

    if st.button('Create Channel'):
        res = backend.create_alert_channel(user_code, {
            'channel_name': channel_name,
            'channel_type': channel_type,
            'recipient': recipient,
            'remarks': remarks
        })
        st.json(res)
        logger.info(res)


# @error_handler
def manage_alert_channel():
    st.markdown("**Manage Channels**")
    _channels = backend.get_alert_channels(user_code=user_code)
    if _channels.empty:
        st.info(f'No channels has been created yet.')
    else:
        st.dataframe(_channels, hide_index=True, column_config=_channel_column_config, column_order=_channel_column_config.keys())


# =================================================
# Display Tabs
# =================================================
manage_alert_channel()
st.divider()
create_alert_channel()
