import os
import json
import pytz
import requests
import streamlit as st

import logging
logger = logging.getLogger()

USER_API_SERVICE = os.getenv('USER_API', 'http://config-api:8000')
tz = pytz.timezone('Asia/Kolkata')

# =============================================================================
# MANAGE User & Client
# =============================================================================
def create_user(data):
    url = f"{USER_API_SERVICE}/create/user"
    res = requests.post(url, data=json.dumps(data))

    if res.status_code == 200:
        # clear cache
        get_users.clear()
        get_user.clear()
        return res.json().get('data')
    else:
        return None

@st.cache_data(ttl=3600)
def get_users(filters):
    url = f"{USER_API_SERVICE}/fetch/user/list"
    logger.debug(f"fetching: {url}")
    res = requests.get(url, params=filters).json()
    return res.get('data')

@st.cache_data(ttl=3600)
def get_user(user_code):
    url = f"{USER_API_SERVICE}/fetch/user/{user_code}"
    logger.debug(f"fetching: {url}")
    res = requests.get(url).json()
    return res.get('data')
