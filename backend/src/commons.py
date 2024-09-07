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

logging.basicConfig(level='INFO', format='%(message)s', datefmt="[%X]",  handlers=[RichHandler()])
logger = logging.getLogger()
