"""
Created On: January 2025
Created By: Sourav Saha
"""
import requests

def check_status(monitor_body: dict) -> tuple[bool, int]:
    try:
        res = requests.request(
            monitor_body.get('method'), monitor_body.get('url'),
            headers=monitor_body.get('headers'),
            params=monitor_body.get('params'),
            data=monitor_body.get('body'),
            verify=False,
            timeout=monitor_body.get('timeout', 10)
        )
        return True, res.status_code

    # handle name resolution error
    except requests.exceptions.ConnectionError as e:
        # logger.error(f"Connection Error: {e}")
        return False, -1

    # handle timeout error
    except requests.exceptions.Timeout as e:
        # logger.error(f"Timeout Error: {e}")
        return False, -2

    # handle other exceptions
    except Exception as e:
        # logger.error(f"Error: {e}")
        return False, -10
