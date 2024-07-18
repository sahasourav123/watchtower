"""
Created On: July 2024
Created By: Sourav Saha
"""
import os
import logging
from rich.logging import RichHandler

# load environment variables
from dotenv import load_dotenv
base_dir = os.path.dirname(os.getcwd())
load_dotenv(f"{base_dir}/.env")
load_dotenv(f"{base_dir}/.env.local", override=True)

logging.basicConfig(level='INFO', format='%(message)s', datefmt="[%X]",  handlers=[RichHandler(keywords=['load-test', 'stress-test', 'baseline'])])
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
