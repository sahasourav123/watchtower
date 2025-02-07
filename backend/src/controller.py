import os
import re
import time
import yaml
from utils.commons import logger

import data_model as dm
import scheduler as sch
import query_engine as qe
from utils.db_util import DatabaseManager
from monitors import apis, sites, servers, databases

db = DatabaseManager()
with open('config.yaml') as config_file:
    config = yaml.safe_load(config_file)

def create_monitor(user_code: str, monitor_type: dm.MonitorTypes, monitor_data: dm.MonitorModel) -> int:
    data = {**monitor_data.model_dump(), 'monitor_type': monitor_type, 'user_code': user_code}
    # insert into database
    monitor_id = qe.insert_monitor(data)
    # schedule monitoring
    sch.create_job(monitor_id, monitor_data.interval, monitor_data.interval_unit, monitor_data.expiry)
    return monitor_id

# update monitor
def update_monitor(user_code: str, monitor_id: int, monitor_data: dm.MonitorModel) -> bool:
    count = qe.update_monitor(user_code, monitor_id, monitor_data.model_dump(exclude_none=True))

    if count > 0 and monitor_data.interval:
        sch.create_job(monitor_id, monitor_data.interval, monitor_data.interval_unit, monitor_data.expiry)
    elif count > 0 and monitor_data.is_active is False:
        sch.manage_job('pause', monitor_id)
    elif count > 0 and monitor_data.is_active:
        sch.manage_job('resume', monitor_id)

    return True

# delete monitor
def delete_monitor(user_code: str, monitor_id: int):
    count = qe.delete_monitor(user_code, monitor_id)
    if count > 0:
        sch.manage_job('delete', monitor_id)
    return {"status": "success"}

def run_monitor(monitor_type: str, monitor_body: dict) -> dict:
    target = monitor_body.get('url') or monitor_body.get('host')
    if not target:
        return {
            'is_success': False,
            'response_code': None,
            'response_time_ms': None,
            'message': 'Invalid monitor body'
        }

    # SSRF
    blacklist = config.get('blacklist', []) + os.getenv('BLACKLIST_HOSTS', '').split(',')
    for item in blacklist:
        if bool(re.search(item, target)):
            return {
                'is_success': False,
                'response_code': None,
                'response_time_ms': None,
                'message': 'Target Blacklisted'
            }

    start_time = time.time()
    try:
        match monitor_type.lower():
            case 'api':
                outcome, response = apis.check_status(monitor_body)
            case  'website':
                outcome, response = sites.check_website(monitor_body['host'])
            case 'domain':
                outcome, response = sites.check_domain_expiry(monitor_body['host'])
            case 'database':
                outcome, response = databases.check_status(monitor_body['host'])
            case 'ssl':
                outcome, response = sites.check_certificate_expiry(monitor_body['host'])
            case 'tcp':
                host, port = monitor_body['host'].split(':')
                outcome, response = servers.check_tcp(host, int(port))
            case 'dns':
                outcome, response = sites.check_dns(monitor_body['host'], monitor_body.get('record_type'), monitor_body.get('nameservers'))
            case _:
                # default case
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
    try:
        result = run_monitor(monitor_type, monitor['monitor_body'])
        # print(f"Executed Monitor ID: {monitor_id}")
    except Exception as e:
        logger.error(f"Error running monitor: {monitor_id} | {str(e)}")
        return False

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
    sql = f"""insert into run_history (monitor_id, outcome, response_time, response, created_at) 
    values ({monitor_id}, {outcome}, {result['response_time_ms'] or 0}, {result['response_code']}, current_timestamp)
    """
    db.insert(sql)
    return outcome


def refresh_monitor():
    df = qe.get_all_monitors()
    for idx, row in df.iterrows():
        sch.create_job(row['monitor_id'], row['interval'], row['interval_unit'], row['expiry'], rerun=False)

    return df.shape[0]
