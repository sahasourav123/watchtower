import utils
from utils import logger
import streamlit as st
from svc import svc_backend as backend

st.header("Monitors")

import auth
user_code = auth.ensure_logged_in(required_access_level='viewer')

monitor_type = st.selectbox('Select Monitor Type', ['api', 'website', 'server'], index=0)

sample_curl = """curl --location 'https://watchtower.finanssure.com/api/v1' \
--header 'Authorization:Bearer XXXXX==' \
--header 'version: 1'
"""
cc = st.columns(2)
query = cc[0].text_area('Insert cURL', value=sample_curl, height=150)
monitor_body = utils.parse_curl_command(query)
cc[1].write('Parsed cURL')
cc[1].code(f"Method:\t {monitor_body.get('method')} \nURL:\t {monitor_body.get('url')}  \nHeaders: {monitor_body.get('headers')}  \nParams:\t {monitor_body.get('params')}  \nBody:\t {monitor_body.get('body')}", language='bash')

monitor_name = st.text_input('Monitor Name', placeholder='Enter Monitor Name')

cc = st.columns(2)
monitor_timeout = cc[0].number_input('Request Timeout (seconds)', value=5)
monitor_interval = cc[1].number_input('Monitor Interval (minutes)', value=5)

# Expectation
test_response = st.radio('Test Response Codes', ['Response Codes - Success', 'Response Codes - Failure'], index=0, horizontal=True)
all_response_codes = [200, 201, 202, 204, 301, 302, 304, 400, 401, 403, 404, 500, 502, 503, 504]
if test_response == 'Response Codes - Success':
    is_allow_list = True
    default_response_codes = [200, 201, 202, 204]
else:
    is_allow_list = False
    default_response_codes = [400, 401, 403, 404, 500, 502, 503, 504]

selected_response_codes = st.multiselect('Response Codes', all_response_codes, default=default_response_codes)
monitor_expectation = {
    'is_allow_list': is_allow_list,
    'response_codes': selected_response_codes
}

alerts = st.multiselect('Alerts', ['slack', 'email', 'telegram'])

cc = st.columns([1, 1, 5])
if cc[0].button('Test Monitor'):
    _url = monitor_body.get('url')
    if _url in [None, '']:
        st.warning('Enter valid cURL command')
    else:
        utils.test_monitor_config(monitor_body)

if cc[1].button('Create Monitor', type='primary'):
    _url = monitor_body.get('url')
    if _url == 'https://watchtower.finanssure.com/api/v1':
        st.warning('Default URL, change the URL')
    elif _url in [None, '']:
        st.warning('Enter valid cURL command')
    else:
        res = backend.create_monitor(monitor_type, monitor_name, monitor_body, monitor_timeout, monitor_interval * 60, monitor_expectation, alerts, user_code, st.session_state.get('org_code'))
        st.json(res)
