import os
import json
import requests
import streamlit as st
from utils import logger

BACKEND_SERVICE = os.getenv('BACKEND_SERVICE', 'http://backend:8000/api/v1')

@st.cache_data(ttl=1800)
def load_service():
    logger.info(f"Checking Backend Service: {BACKEND_SERVICE}")
    res = requests.get(BACKEND_SERVICE)
    return res.json()

def create_monitor(monitor_type, monitor_name, monitor_body, timeout, frequency, monitor_expectation, alerts):
    url = f'{BACKEND_SERVICE}/create/monitor?monitor_type={monitor_type}'
    monitor_data = {
        'monitor_name': monitor_name,
        'monitor_body': monitor_body,
        'timeout': timeout,
        'frequency': frequency,
        'expectation': monitor_expectation,
        'alerts': alerts
    }
    res = requests.post(url, data=json.dumps(monitor_data), headers={'Content-Type': 'application/json'})

    # clear cache if successful
    if res.status_code == 200:
        fetch_monitors.clear()

    return res.json()

@st.cache_data(ttl=300)
def fetch_monitors(filters: dict):
    url = f'{BACKEND_SERVICE}/fetch/monitor'
    res = requests.get(url, params=filters)
    if res.status_code != 200:
        return []

    data = res.json()['data']
    return data
