import os
import json
import pandas as pd
from datetime import date
import requests
import streamlit as st
from utils import logger

BACKEND_SERVICE = os.getenv('BACKEND_SERVICE', 'http://backend:8000')
PUBLIC_ROUTE = f"{BACKEND_SERVICE}/api/public/v1"
INTERNAL_ROUTE = f"{BACKEND_SERVICE}/internal/v1"

@st.cache_data(ttl=1800)
def load_service():
    logger.info(f"Checking Backend Service: {PUBLIC_ROUTE}")
    res = requests.get(PUBLIC_ROUTE)
    return res.json()

def check_monitor(monitor_type: str, monitor_body: dict):
    url = f"{PUBLIC_ROUTE}/check?monitor_type={monitor_type}"
    res = requests.get(url, json=monitor_body)
    return res.json()

def run_monitor(user_code: str, monitor_id: int):
    url = f"{INTERNAL_ROUTE}/run/monitor/{monitor_id}?user_code={user_code}"
    res = requests.get(url)
    return res.json()

def create_monitor(user_code, monitor_type, monitor_config: dict):
    url = f'{INTERNAL_ROUTE}/create/monitor?user_code={user_code}&monitor_type={monitor_type}'
    res = requests.post(url, json=monitor_config, headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if res.status_code in [200, 201]:
        fetch_monitors.clear()

    return res.json()

def update_monitor(user_code, monitor_id, monitor_data):
    url = f'{INTERNAL_ROUTE}/update/monitor/{monitor_id}?user_code={user_code}'
    res = requests.put(url, data=json.dumps(monitor_data), headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if res.status_code in [200, 201]:
        fetch_monitors.clear()

    return res.json()

def delete_monitor(user_code, monitor_id):
    url = f'{INTERNAL_ROUTE}/delete/monitor/{monitor_id}?user_code={user_code}'
    res = requests.delete(url)

    # clear cache if successful
    if res.status_code in [200, 201]:
        fetch_monitors.clear()

    return res.json()

def _fetch_api_data(url, params) -> pd.DataFrame:
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return pd.DataFrame()

    data = res.json()['data']
    if len(data) == 0:
        return pd.DataFrame()
    return pd.DataFrame(data)

@st.cache_data(ttl=60)
def fetch_monitors(user_code: str):
    if user_code == 'guest':
        endpoint = f"{PUBLIC_ROUTE}/fetch/monitor"
        return _fetch_api_data(endpoint, params=None)

    endpoint = f"{INTERNAL_ROUTE}/fetch/monitor"
    return _fetch_api_data(endpoint, params={'user_code': user_code})

@st.cache_data(ttl=60)
def fetch_monitor_history(user_code: str, limit: int):
    if user_code == 'guest':
        endpoint = f"{PUBLIC_ROUTE}/fetch/history"
        return _fetch_api_data(endpoint, params={'limit': limit})

    endpoint = f"{INTERNAL_ROUTE}/fetch/history"
    return _fetch_api_data(endpoint, params={'user_code': user_code, 'limit': limit})

@st.cache_data(ttl=60)
def fetch_uptime_history(user_code, day_limit):
    endpoint = f"{PUBLIC_ROUTE}/fetch/uptime" if user_code == 'guest' else f"{INTERNAL_ROUTE}/fetch/uptime"
    return _fetch_api_data(endpoint, params={'user_code': user_code, 'day_limit': day_limit})


# ==============================================================
# STATS
# ==============================================================
@st.cache_data(ttl=60)
def get_monitor_stats(user_code: str):
    if user_code == 'guest':
        res = requests.get(f"{PUBLIC_ROUTE}/stats/global")
    else:
        res = requests.get(f"{INTERNAL_ROUTE}/stats/monitor?user_code={user_code}")
    return res.json()['data']

@st.cache_data(ttl=60)
def get_daily_response_stats(user_code: str, day_limit: int):
    if user_code == 'guest':
        res = requests.get(f"{PUBLIC_ROUTE}/stats/response/daily?day_limit=1000")
    else:
        res = requests.get(f"{INTERNAL_ROUTE}/stats/response/daily?user_code={user_code}&day_limit={day_limit}")

    return pd.DataFrame(res.json()['data'])

@st.cache_data(ttl=60)
def get_agg_response_stats(user_code: str):
    if user_code == 'guest':
        res = requests.get(f"{PUBLIC_ROUTE}/stats/response/aggregated")
    else:
        res = requests.get(f"{INTERNAL_ROUTE}/stats/response/aggregated?user_code={user_code}")

    return pd.DataFrame(res.json()['data'])

@st.cache_data(ttl=60)
def get_execution_stats():
    res = requests.get(f"{PUBLIC_ROUTE}/stats/execution")
    result = res.json()
    return result['agg'], pd.DataFrame(result['data']).set_index('date')

# ==============================================================
# ALERTS
# ==============================================================
def slack_oauth_callback(user_code: str, access_code: str):
    response = requests.post(
        'https://slack.com/api/oauth.v2.access',
        data={
            'client_id': os.getenv('SLACK_CLIENT_ID'),
            'client_secret': os.getenv('SLACK_CLIENT_SECRET'),
            'code': access_code,
            'redirect_uri': os.getenv('SLACK_REDIRECT_URI')
        }
    )
    result = response.json()
    if not result.get('ok'):
        return result

    alert_recipient = {
        "channel_type": "slack",
        "channel_name": f"{result['team']['name']} - {result['incoming_webhook']['channel']}",
        "recipient": result['incoming_webhook'],
    }
    return create_alert_channel(user_code, data=alert_recipient)

def create_alert_channel(user_code, data):
    url = f"{INTERNAL_ROUTE}/create/channel?user_code={user_code}"
    res = requests.post(url, json=data, headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if res.status_code in [200, 201]:
        get_alert_channels.clear()

    return res.json()

@st.cache_data(ttl=120)
def get_alert_channels(user_code):
    channel_df = _fetch_api_data(f"{INTERNAL_ROUTE}/fetch/channel", params={'user_code': user_code})

    # if channel type is 'slack' then extract channel_id from recipient
    def extract_recipient(row):
        if row['channel_type'] == 'email':
            return row['recipient']['mail']
        elif row['channel_type'] == 'slack':
            return row['recipient']['channel_id']
        else:
            return row['recipient']['url']

    if not channel_df.empty:
        channel_df['recipient'] = channel_df.apply(extract_recipient, axis=1)
    return channel_df

# ==============================================================
# API TOKENS
# ==============================================================

@st.cache_data(ttl=600)
def fetch_tokens(user_code):
    url = f"{INTERNAL_ROUTE}/fetch/token?user_code={user_code}"
    res = requests.get(url)
    return pd.DataFrame(res.json()['data'])

def create_token(user_code, name, permission, expiry_days=60):
    url = f"{INTERNAL_ROUTE}/create/token?user_code={user_code}"
    data = {
        'name': name,
        'permission': permission,
        'expiry_days': expiry_days
    }
    res = requests.post(url, params=data, headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if res.status_code in [200, 201]:
        fetch_tokens.clear()
        logger.info(f"Token created with permission: {permission} and expiry: {expiry_days} days | User: {user_code}")

    return res.json()

def delete_token(user_code, token):
    url = f"{INTERNAL_ROUTE}/delete/token?user_code={user_code}&token={token}"
    res = requests.delete(url)

    # clear cache if successful
    if res.status_code in [200, 201]:
        fetch_tokens.clear()
        logger.info(f"Token deleted: {res.json()}| User: {user_code}")

    return res.json()
