import time
import requests
from commons import logger
from db_util import DatabaseManager

db = DatabaseManager()

def get_monitor_by_id(monitor_id: int):
    sql = f"select * from monitors where monitor_id={monitor_id}"
    _df = db.query(sql)
    monitor = _df.to_dict('records')[0]
    return monitor

def get_monitor_by_orgid(org_id: int):
    sql = f"select * from monitors where org_id={org_id}"
    return db.query(sql)

def get_all_monitors():
    sql = "select * from monitors where is_active"
    df = db.query(sql)
    return df

def insert_monitor(data: dict):
    logger.info(f"Creating monitor: {data}")
    sql = """insert into monitors (monitor_type, monitor_name, monitor_body, timeout, interval, expectation, alerts)
    values (%(monitor_type)s, %(monitor_name)s, %(monitor_body)s, %(timeout)s, %(frequency)s, %(expectation)s, %(alerts)s)
    returning monitor_id
    """
    monitor_id = db.insert(sql, data)
    logger.info(f"Inserted Monitor with id {monitor_id}")
    return monitor_id

def update_monitor(monitor_id: int, data: dict):
    logger.info(f"Updating monitor: {data}")
    logger.info(f"Updated Monitor with id {monitor_id}")
    pass

def delete_monitor(monitor_id: int):
    logger.info(f"Deleting monitor: #{monitor_id}")
    sql = f"delete from monitors where monitor_id = {monitor_id}"
    db.query(sql)
    logger.info(f"Deleted Monitor with id {monitor_id}")

def run_monitor_by_id(monitor_id):
    monitor = get_monitor_by_id(monitor_id)
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
    response_time = time.time() - start_time
    sql = f"""insert into run_history (org_id, monitor_id, outcome, response_time, response) values 
    ({monitor['org_id']}, {monitor_id}, {outcome}, {response_time}, '{response}')
    """
    db.insert(sql)
    return outcome

def run_api_monitor(monitor_body: dict, expectation: dict):
    res = requests.request(
        monitor_body.get('method'), monitor_body.get('url'),
        headers=monitor_body.get('headers'),
        params=monitor_body.get('params'),
        data=monitor_body.get('body')
    )
    logger.info(f"Response: {res.status_code} | {res.reason}")

    if expectation:
        response_code_list = expectation.get('response_codes')
        is_allow_list = expectation.get('is_allow_list')
        outcome = (is_allow_list and res.status_code in response_code_list) or (not is_allow_list and res.status_code not in response_code_list)

    else:
        outcome = 200 <= res.status_code < 300

    return outcome, res.status_code
