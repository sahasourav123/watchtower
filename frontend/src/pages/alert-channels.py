"""
Created on: 23 Sep 2024
@author: SouravS
"""
import os
import json
import streamlit as st
import auth
import logging

from svc import svc_backend as backend

logger = logging.getLogger()

st.set_page_config(layout='wide', page_title='Alert Groups', initial_sidebar_state='expanded')

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
    channel_type = st.selectbox('Channel Type', options=['email', 'webhook'], index=0)
    recipient = None

    if channel_type == 'email':
        _input_ = st.text_input('Destination', placeholder='e.g. foo.bar@example.com')
        recipient = {'mail': _input_} if _input_ else None

    elif channel_type == 'webhook':
        url = st.text_input('Destination', placeholder='e.g. https://my-webhook-url.com')
        method = st.selectbox('Method', options=['POST', 'GET'], index=0)
        headers = st.text_area('Headers', placeholder='e.g. {"Authorization": "Bearer my-token"}')
        try:
            recipient = {
                "url": url,
                "method": method,
                "headers": json.loads(headers) if headers else {},
            } if url else None
        except json.JSONDecodeError as e:
            st.error(f"Invalid Headers: {e}")
            recipient = None

    remarks = st.text_input('Remarks')

    if st.button(':material/add: Create Channel') and recipient:
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
st.divider()

# add to slack button
auth_url = f"https://slack.com/oauth/v2/authorize?client_id={os.getenv('SLACK_CLIENT_ID')}&scope=incoming-webhook&user_scope=&redirect_uri={os.getenv('SLACK_REDIRECT_URI')}"
st.markdown(f"""<a href="{auth_url}"><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcSet="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>""", unsafe_allow_html=True)

# =================================================
# Handle OAuth Callback
# =================================================
if 'code' in st.query_params and user_code != 'guest':
    code = st.query_params.get('code')
    if code:
        res = backend.slack_oauth_callback(user_code, code)
        st.json(res)

    # clear request params after processing
    st.query_params.clear()
