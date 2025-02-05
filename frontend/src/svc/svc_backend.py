import os
import json
import pandas as pd
from datetime import date
import requests
import streamlit as st
from utils import logger

BACKEND_SERVICE = os.getenv('BACKEND_SERVICE', 'http://backend:8000')
PUBLIC_ROUTE = f"{BACKEND_SERVICE}/api/v1"
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

def get_stats(user_code: str):
    if user_code == 'guest':
        res = requests.get(f"{PUBLIC_ROUTE}/stats/global")
    else:
        res = requests.get(f"{INTERNAL_ROUTE}/stats?user_code={user_code}")
    return res.json()['data']

def create_monitor(monitor_type, monitor_name, monitor_body, timeout, interval, interval_unit, expiry: date, monitor_expectation, alerts, user_code, org_code=None):
    url = f'{INTERNAL_ROUTE}/create/monitor?user_code={user_code}&monitor_type={monitor_type}'
    monitor_data = {
        'monitor_name': monitor_name,
        'monitor_body': monitor_body,
        'timeout': timeout,
        'interval': interval,
        'interval_unit': interval_unit,
        'expiry': expiry.strftime('%Y-%m-%d') if expiry else None,
        'expectation': monitor_expectation,
        'alerts': alerts,
    }
    res = requests.post(url, json=monitor_data, headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if 200 >= res.status_code >= 201:
        fetch_monitors.clear()

    return res.json()

def update_monitor(user_code, monitor_id, monitor_data):
    url = f'{INTERNAL_ROUTE}/update/monitor/{monitor_id}?user_code={user_code}'
    res = requests.put(url, data=json.dumps(monitor_data), headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if 200 >= res.status_code >= 201:
        fetch_monitors.clear()

    return res.json()

def delete_monitor(user_code, monitor_id):
    url = f'{INTERNAL_ROUTE}/delete/monitor/{monitor_id}?user_code={user_code}'
    res = requests.delete(url)

    # clear cache if successful
    if 200 >= res.status_code >= 201:
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
def create_alert_channel(user_code, data):
    url = f"{INTERNAL_ROUTE}/create/channel?"
    res = requests.post(url, data=json.dumps({'user_code': user_code, **data}), headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if 200 >= res.status_code >= 201:
        get_alert_channels.clear()

    return res.json()

@st.cache_data(ttl=300)
def get_alert_channels(user_code):
    return _fetch_api_data(f"{INTERNAL_ROUTE}/fetch/channel", params={'user_code': user_code})
