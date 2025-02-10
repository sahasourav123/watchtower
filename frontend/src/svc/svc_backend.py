import os
import json
import pandas as pd
from datetime import date
import requests
import streamlit as st
from utils import logger

BACKEND_SERVICE = os.getenv('BACKEND_SERVICE', 'http://backend:8000')
PUBLIC_ROUTE = f"{BACKEND_SERVICE}/public/v1"
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

def get_stats(user_code: str):
    if user_code == 'guest':
        res = requests.get(f"{PUBLIC_ROUTE}/stats/global")
    else:
        res = requests.get(f"{INTERNAL_ROUTE}/stats?user_code={user_code}")
    return res.json()['data']

def create_monitor(monitor_type, monitor_group, monitor_name, monitor_body, timeout, interval, interval_unit, expiry: date, monitor_expectation, alerts, monitor_tags, user_code, org_code=None):
    url = f'{INTERNAL_ROUTE}/create/monitor?user_code={user_code}&monitor_type={monitor_type}'
    monitor_data = {
        'monitor_name': monitor_name,
        'monitor_group': monitor_group,
        'monitor_body': monitor_body,
        'timeout': timeout,
        'interval': interval,
        'interval_unit': interval_unit,
        'expiry': expiry.strftime('%Y-%m-%d') if expiry else None,
        'expectation': monitor_expectation,
        'alerts': alerts,
        'tags': [tag.strip() for tag in monitor_tags.split(',')],
    }
    res = requests.post(url, json=monitor_data, headers={'Content-Type': 'application/json'})

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
    endpoint = f"{PUBLIC_ROUTE}/fetch/monitor" if user_code == 'guest' else f"{INTERNAL_ROUTE}/fetch/monitor"
    return _fetch_api_data(endpoint, params={'user_code': user_code})

def fetch_monitor_history(user_code: str, limit: int):
    endpoint = f"{PUBLIC_ROUTE}/fetch/history" if user_code == 'guest' else f"{INTERNAL_ROUTE}/fetch/history"
    return _fetch_api_data(endpoint, params={'user_code': user_code, 'limit': limit})

@st.cache_data(ttl=60)
def fetch_uptime_history(user_code, day_limit):
    endpoint = f"{PUBLIC_ROUTE}/fetch/uptime" if user_code == 'guest' else f"{INTERNAL_ROUTE}/fetch/uptime"
    return _fetch_api_data(endpoint, params={'user_code': user_code, 'day_limit': day_limit})

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
