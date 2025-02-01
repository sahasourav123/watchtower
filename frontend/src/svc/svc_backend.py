import os
import json
import pandas as pd
from datetime import date
import requests
import streamlit as st
from utils import logger

BACKEND_SERVICE = os.getenv('BACKEND_SERVICE', 'http://backend:8000/api/v1')

@st.cache_data(ttl=1800)
def load_service():
    logger.info(f"Checking Backend Service: {BACKEND_SERVICE}")
    res = requests.get(BACKEND_SERVICE)
    return res.json()

def check_monitor(monitor_type: str, monitor_body: dict):
    url = f"{BACKEND_SERVICE}/check?monitor_type={monitor_type}"
    res = requests.get(url, json=monitor_body)
    return res.json()

def get_stats(user_code: str):
    res = requests.get(f"{BACKEND_SERVICE}/stats?user_code={user_code}")
    return res.json()['data']

def create_monitor(monitor_type, monitor_name, monitor_body, timeout, interval, interval_unit, expiry: date, monitor_expectation, alerts, user_code, org_code=None):
    url = f'{BACKEND_SERVICE}/create/monitor?monitor_type={monitor_type}'
    monitor_data = {
        'monitor_name': monitor_name,
        'monitor_body': monitor_body,
        'timeout': timeout,
        'interval': interval,
        'interval_unit': interval_unit,
        'expiry': expiry.strftime('%Y-%m-%d') if expiry else None,
        'expectation': monitor_expectation,
        'alerts': alerts,
        'user_code': user_code,
        'org_code': org_code
    }
    res = requests.post(url, json=monitor_data, headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if 200 >= res.status_code >= 201:
        fetch_monitors.clear()

    return res.json()

def update_monitor(monitor_id, monitor_data):
    url = f'{BACKEND_SERVICE}/update/monitor/{monitor_id}'
    res = requests.put(url, data=json.dumps(monitor_data), headers={'Content-Type': 'application/json'})

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

def fetch_monitors(filters: dict):
    return _fetch_api_data(url=f'{BACKEND_SERVICE}/fetch/monitor', params=filters)

def fetch_monitor_history(filters: dict):
    return _fetch_api_data(url=f'{BACKEND_SERVICE}/fetch/recent/monitor', params=filters)

@st.cache_data(ttl=300)
def fetch_uptime_history(user_code, day_limit):
    return _fetch_api_data(url=f'{BACKEND_SERVICE}/fetch/uptime', params={'user_code': user_code, 'day_limit': day_limit})

# ==============================================================
# ALERTS
# ==============================================================
def create_alert_channel(user_code, data):
    url = f"{BACKEND_SERVICE}/create/channel?"
    res = requests.post(url, data=json.dumps({'user_code': user_code, **data}), headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if 200 >= res.status_code >= 201:
        get_alert_channels.clear()

    return res.json()

@st.cache_data(ttl=300)
def get_alert_channels(user_code):
    return _fetch_api_data(f"{BACKEND_SERVICE}/fetch/channel", params={'user_code': user_code})
