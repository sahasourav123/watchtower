import os
import json
import pandas as pd
import requests
import streamlit as st
from utils import logger

BACKEND_SERVICE = os.getenv('BACKEND_SERVICE', 'http://backend:8000/api/v1')

@st.cache_data(ttl=1800)
def load_service():
    logger.info(f"Checking Backend Service: {BACKEND_SERVICE}")
    res = requests.get(BACKEND_SERVICE)
    return res.json()

def create_monitor(monitor_type, monitor_name, monitor_body, timeout, interval, monitor_expectation, alerts, user_code, org_code=None):
    url = f'{BACKEND_SERVICE}/create/monitor?monitor_type={monitor_type}'
    monitor_data = {
        'monitor_name': monitor_name,
        'monitor_body': monitor_body,
        'timeout': timeout,
        'interval': interval,
        'expectation': monitor_expectation,
        'alerts': alerts,
        'user_code': user_code,
        'org_code': org_code
    }
    res = requests.post(url, data=json.dumps(monitor_data), headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if 200 >= res.status_code >= 201:
        fetch_monitors.clear()

    return res.json()

@st.cache_data(ttl=300)
def fetch_monitors(filters: dict):
    url = f'{BACKEND_SERVICE}/fetch/monitor'
    res = requests.get(url, params=filters)
    if res.status_code != 200:
        return []

    data = res.json()['data']
    if len(data) == 0:
        return pd.DataFrame()
    return pd.DataFrame(data)

def fetch_monitor_history(filters: dict):
    url = f'{BACKEND_SERVICE}/fetch/recent/monitor'
    res = requests.get(url, params=filters)
    if res.status_code != 200:
        return []

    data = res.json()['data']
    print(data)
    if len(data) == 0:
        return pd.DataFrame()
    return pd.DataFrame(data)
