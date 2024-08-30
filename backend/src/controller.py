from utils import logger
from utils import DatabaseManager

db = DatabaseManager()

def create_monitor(data: dict):
    logger.info(f"Creating monitor: {data}")
    sql = """insert into monitors (monitor_type, monitor_name, monitor_body, timeout, frequency, expectation, alerts)
    values (%(monitor_type)s, %(monitor_name)s, %(monitor_body)s, %(timeout)s, %(frequency)s, %(expectation)s, %(alerts)s)
    returning monitor_id
    """
    monitor_id = db.insert(sql, data)
    return monitor_id
