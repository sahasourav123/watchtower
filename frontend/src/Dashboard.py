"""
Created On: July 2024
Created By: Sourav Saha
"""
import utils
from utils import logger
import streamlit as st
from svc import svc_backend as backend
from __version__ import __version__

# ======================================================================
# Start Application
# ======================================================================
st.set_page_config(layout='wide', page_title='The Watchtower', initial_sidebar_state='expanded')
st.title(f'The Watchtower')
logger.info("initializing app")
svc = backend.load_service()
st.subheader(f"*Frontend: {__version__} | Backend: {svc['version']}*")

style = """
div.stButton button {
    width: 150px;
}
"""
st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

monitor_type = st.selectbox('Select Monitor Type', ['api', 'website', 'server'], index=0)

sample_curl = """curl --location 'https://api.example.com/path?foo=bar&hello=world' \
--header 'Authorization:Bearer XXXXX==' \
--header 'version: 2'
"""
cc = st.columns(2)
query = cc[0].text_area('Insert cURL', value=sample_curl, height=150)
monitor_body = utils.parse_curl_command(query)
cc[1].write('Parsed cURL')
cc[1].code(f"Method:\t {monitor_body.get('method')} \nURL:\t {monitor_body.get('url')}  \nHeaders: {monitor_body.get('headers')}  \nParams:\t {monitor_body.get('params')}  \nBody:\t {monitor_body.get('body')}", language='bash')

monitor_name = st.text_input('Monitor Name', value='Monitor Name')
monitor_timeout = st.number_input('Monitor Timeout', value=5)
monitor_frequency = st.number_input('Monitor Frequency (Minutes)', value=5)

# Expectation
response_code_type = st.radio('Expect Response Codes', ['Response Code - Allowed', 'Response Code - Not Allowed'], index=0, horizontal=True)
response_codes = [200, 201, 202, 204, 301, 302, 304, 400, 401, 403, 404, 500, 502, 503, 504]
if response_code_type == 'Response Code - Allowed':
    default_response_codes = [200, 201, 202, 204]
else:
    default_response_codes = [400, 401, 403, 404, 500, 502, 503, 504]
selected_response_codes = st.multiselect('Response Codes', response_codes, default=default_response_codes)
monitor_expectation = {
    'response_code_type': response_code_type,
    'response_codes': selected_response_codes
}

alerts = st.multiselect('Alerts', ['slack', 'email', 'telegram'])

cc = st.columns(2)
if cc[0].button('Test Monitor'):
    import requests
    res = requests.request(monitor_body.get('method'), monitor_body.get('url'), headers=monitor_body.get('headers'), params=monitor_body.get('params'), data=monitor_body.get('body'))
    st.write(f"Response: {res.status_code} | {res.reason}")
    st.write(res.json())

if cc[1].button('Create Monitor', type='primary'):
    _url = monitor_body.get('url')
    if _url == 'https://api.example.com/path':
        st.warning('Default URL, change the URL')
    elif _url in [None, '']:
        st.warning('Enter valid cURL command')
    else:
        res = backend.create_monitor(monitor_type, monitor_name, monitor_body, monitor_timeout, monitor_frequency * 60, monitor_expectation, alerts)
        st.json(res)
