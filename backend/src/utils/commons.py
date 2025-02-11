"""
Created On: July 2024
Created By: Sourav Saha
"""
import os
import logging
from rich.logging import RichHandler

import hmac, hashlib
from functools import lru_cache

# load environment variables
# from dotenv import load_dotenv
# base_dir = os.path.dirname(os.getcwd())
# load_dotenv(f"{base_dir}/.env")
# load_dotenv(f"{base_dir}/.env.local", override=True)

logging.basicConfig(level='INFO', format='%(message)s', datefmt="[%X]",  handlers=[RichHandler()])
logger = logging.getLogger()

HASH_KEY = os.getenv('MONITOR_HASH_KEY').encode('utf-8')

@lru_cache(maxsize=1000)
def compute_hash(input_string) -> str:
    return hmac.new(HASH_KEY, str(input_string).encode('utf-8'), hashlib.md5).hexdigest()
