"""
Created On: July 2024
Created By: Sourav Saha
"""
import os
import logging
from rich.logging import RichHandler

import shlex
import requests
from urllib.parse import urlparse, parse_qs

# load environment variables
from dotenv import load_dotenv
base_dir = os.path.dirname(os.getcwd())
load_dotenv(f"{base_dir}/.env")
load_dotenv(f"{base_dir}/.env.local", override=True)

logging.basicConfig(level='INFO', format='%(message)s', datefmt="[%X]",  handlers=[RichHandler()])
logger = logging.getLogger()

import streamlit as st
import traceback

# context manager for error handling
def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.error(f"ValueError: {str(e)}")
            st.warning(f"{str(e)}")
            return None
        except Exception as e:
            logger.exception(f"Error: {str(e)}")
            st.error(f"**{type(e).__name__}**: {str(e)}")
            st.code(f"{traceback.format_exc()}")
            return None

    return wrapper

# parse curl command
@st.cache_data(ttl=1800)
def parse_curl_command(curl_command):
    # Split the curl command into a list of tokens
    # remove line breaks
    curl_command = curl_command.replace('\\\n', '')
    # split by space but preserve within quotes
    tokens = shlex.split(curl_command)

    # Initialize variables to store URL, headers, request params, and body
    method = 'GET'
    url = None
    headers = {}
    params = {}
    body = None

    # Iterate over the tokens to extract information
    for i in range(len(tokens)):
        if tokens[i].startswith('http'):
            # Extract the URL with Params
            url_long = tokens[i]
            parsed_url = urlparse(url_long)
            # Reconstruction of the URL without the query parameters
            url = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
            # Extract the query parameters
            for key, value in parse_qs(parsed_url.query).items():
                params[key] = value[0]

        elif tokens[i] == '-X':
            method = tokens[i + 1]

        elif tokens[i] == '-H' or tokens[i] == '--header':
            # Extract headers
            header = tokens[i + 1].split(':')
            headers[header[0].strip()] = header[1].strip()

        elif tokens[i] == '--data' or tokens[i] == '-d':
            # Extract request body
            body = tokens[i + 1]

        elif tokens[i].startswith('--data-ascii=') or tokens[i].startswith('--data-binary='):
            # Extract request body when using data-ascii or data-binary
            body = tokens[i].split('=', 1)[1]

        elif tokens[i] == '--data-urlencode':
            # Extract request parameters when using data-urlencode
            param = tokens[i + 1].split('=')
            params[param[0].strip()] = param[1].strip()

    return {
        'method': method,
        'url': url,
        'headers': headers,
        'params': params,
        'body': body
    }


def test_monitor_config(monitor_body: dict):
    try:
        res = requests.request(monitor_body.get('method'), monitor_body.get('url'), headers=monitor_body.get('headers'), params=monitor_body.get('params'), data=monitor_body.get('body'))
        st.write(f"Response: {res.status_code} | {res.reason}")
        st.write(res.json())
    except Exception as e:
        st.error(f"Invalid Monitor config \n\n {e.args}")
