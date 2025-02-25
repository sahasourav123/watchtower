"""
Created On: January 2025
Created By: Sourav Saha
"""
from sqlalchemy import create_engine

def check_status(monitor_body: dict) -> tuple[bool, int]:
    conn_str = f"{monitor_body['scheme']}://{monitor_body['username']}:{monitor_body['password']}@{monitor_body['host']}:{monitor_body['port']}/{monitor_body['database']}"

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
