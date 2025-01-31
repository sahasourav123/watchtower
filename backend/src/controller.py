import time
from utils.commons import logger
import query_engine as qe
from utils.db_util import DatabaseManager
from monitors import apis, sites, servers, databases

db = DatabaseManager()

def run_monitor(monitor_type: str, monitor_body: dict) -> dict:
    if 'body' not in monitor_body:
        return {
            'is_success': False,
            'response_code': None,
            'response_time_ms': None
        }

    start_time = time.time()
    try:
        if monitor_type == 'api':
            outcome, response = apis.check_status(monitor_body)
        elif monitor_type == 'website':
            outcome, response = sites.check_status(monitor_body['body'])
        elif monitor_type == 'domain':
            outcome, response = sites.check_domain_expiry(monitor_body['body'])
        elif monitor_type == 'server':
            host, port = monitor_body['body'].split(':')
            outcome, response = servers.check_status(host, int(port))
        elif monitor_type == 'database':
            outcome, response = databases.check_status(monitor_body['body'])
        elif monitor_type == 'ssl':
            outcome, response = sites.check_certificate_expiry(monitor_body['body'])
        else:
            outcome, response = False, 0

    except Exception as e:
        logger.error(f"Error running monitor: {e}")
        outcome, response = False, -10

    response_time_ms = round((time.time() - start_time) * 1000, 2)
    return {
        'is_success': outcome,
        'response_code': response,
        'response_time_ms': response_time_ms
    }


def run_monitor_by_id(monitor_id):
    monitor = qe.get_monitor_by_id(monitor_id)
    monitor_type = monitor['monitor_type']
    result = run_monitor(monitor_type, monitor['monitor_body'])
    outcome = result['is_success']

    if monitor_type == 'api':
        expectation = monitor.get('expectation')
        if expectation:
            response_code_list = expectation.get('response_codes')
            is_allow_list = expectation.get('is_allow_list')
            outcome = (is_allow_list and result['response_code'] in response_code_list) or (not is_allow_list and result['response_code'] not in response_code_list)

        else:
            outcome = 200 <= result['response_code'] < 300

    # store run history
    sql = f"""insert into run_history (monitor_id, outcome, response_time, response) 
    values ({monitor_id}, {outcome}, {result['response_time_ms']}, {result['response_code']})
    """
    db.insert(sql)
    return outcome

