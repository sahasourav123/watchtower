import time
import requests
from utils.commons import logger
import query_engine as qe
from utils.db_util import DatabaseManager

db = DatabaseManager()

def run_monitor_by_id(monitor_id):
    monitor = qe.get_monitor_by_id(monitor_id)
    start_time = time.time()
    try:
        if monitor['monitor_type'] == 'api':
            outcome, response = run_api_monitor(monitor['monitor_body'], monitor.get('expectation'))
        else:
            outcome, response = False

    except Exception as e:
        logger.error(f"Error running monitor: {e}")
        outcome, response = False

    # store run history
    response_time_ms = (time.time() - start_time) * 1000
    sql = f"""insert into run_history (monitor_id, outcome, response_time, response) values 
    ({monitor_id}, {outcome}, {response_time_ms}, '{response}')
    """
    db.insert(sql)
    return outcome

def run_api_monitor(monitor_body: dict, expectation: dict):
    res = requests.request(
        monitor_body.get('method'), monitor_body.get('url'),
        headers=monitor_body.get('headers'),
        params=monitor_body.get('params'),
        data=monitor_body.get('body'),
        verify=False
    )
    logger.info(f"Response: {res.status_code} | {res.reason}")

    if expectation:
        response_code_list = expectation.get('response_codes')
        is_allow_list = expectation.get('is_allow_list')
        outcome = (is_allow_list and res.status_code in response_code_list) or (not is_allow_list and res.status_code not in response_code_list)

    else:
        outcome = 200 <= res.status_code < 300

    return outcome, res.status_code
