"""
Created On: January 2025
Created By: Sourav Saha
"""
from sqlalchemy import create_engine

def check_status(conn_str) -> tuple[bool, int]:
    try:
        engine = create_engine(conn_str)
    except Exception as e:
        return False, -10

    try:
        conn = engine.connect()

    except Exception as e:
        return False, -1

    else:
        conn.close()
        return True, 0
