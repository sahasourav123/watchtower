import os
import json
import pytz
import requests
import streamlit as st

import logging
logger = logging.getLogger()

USER_API_SERVICE = os.getenv('USER_API')
tz = pytz.timezone('Asia/Kolkata')

if not USER_API_SERVICE:
    logger.warning(f"Env Variable USER_API_SERVICE not found. | Authentication workflow won't work.")

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

def log_signin(data):
    url = f"{USER_API_SERVICE}/log/signin"
    res = requests.post(url, data=json.dumps(data))
    logger.info("Signin Event logged")
    return res
