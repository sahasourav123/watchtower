import pandas as pd

from utils.commons import logger
from utils.db_util import DatabaseManager

db = DatabaseManager()

def get_monitors(filters):
    sql = "select * from monitors"
    if filters:
        sql += " where " + " and ".join([f"{k}='{v}'" for k, v in filters.items() if v])
    return db.query(sql)

def get_monitor_by_id(monitor_id: int):
    sql = f"select * from monitors where monitor_id={monitor_id}"
    _df = db.query(sql)
    monitor = _df.to_dict('records')[0]
    return monitor

def get_all_monitors():
    sql = "select * from monitors where is_active"
    df = db.query(sql)
    return df

def insert_monitor(data: dict):
    logger.info(f"Creating monitor: {data}")
    sql = """insert into monitors (monitor_type, monitor_name, monitor_body, timeout, interval, expectation, alerts, user_code, org_id)
    values (%(monitor_type)s, %(monitor_name)s, %(monitor_body)s, %(timeout)s, %(interval)s, %(expectation)s, %(alerts)s, %(user_code)s, %(org_id)s)
    returning monitor_id
    """
    monitor_id = db.insert(sql, data)
    logger.info(f"Inserted Monitor with id {monitor_id}")
    return monitor_id

def update_monitor(monitor_id: int, data: dict):
    logger.info(f"Updating monitor: {data}")
    sql = f"""
        UPDATE monitors SET
            {','.join([f"{key}=%({key})s" for key in data.keys()])}
        WHERE monitor_id = {monitor_id}
        """
    db.update(sql, data)
    logger.info(f"Updated Monitor with id {monitor_id}")

def delete_monitor(monitor_id: int):
    logger.info(f"Deleting monitor: #{monitor_id}")
    sql = f"delete from monitors where monitor_id = {monitor_id}"
    db.query(sql)
    logger.info(f"Deleted Monitor with id {monitor_id}")

# fetch recent history
def fetch_recent_history_by_org(org_id: int, limit: int = 10):
    sql = f"""
    WITH ranked_history AS (
        SELECT monitor_id, outcome, ROW_NUMBER() OVER (PARTITION BY monitor_id ORDER BY created_at DESC) AS rn
        FROM run_history
        where monitor_id in (select monitor_id from monitors where org_id = {org_id}) 
    )
    SELECT monitor_id, string_agg(outcome::text, ' ') AS outcomes
    FROM ranked_history
    WHERE rn <= {limit}
    group by monitor_id
    """
    return db.query(sql)

def fetch_recent_history_by_user(user_code: str, limit: int = 10):
    sql = f"""
    WITH ranked_history AS (
        SELECT monitor_id, outcome, ROW_NUMBER() OVER (PARTITION BY monitor_id ORDER BY created_at DESC) AS rn
        FROM run_history
        where monitor_id in (select monitor_id from monitors where user_code = '{user_code}')
    )
    SELECT monitor_id, string_agg(outcome::text, ' ') AS outcomes
    FROM ranked_history
    WHERE rn <= {limit}
    group by monitor_id
    """
    return db.query(sql)


"""
================================================
ALERT CHANNEL
================================================
"""
def get_alert_channel(user_code) -> pd.DataFrame:
    sql = f"select * from alert_channel where user_code = '{user_code}'"
    return db.query(sql)

def insert_alert_channel(data) -> int:
    sql = """insert into alert_channel (channel_name, channel_type, recipient, remarks, user_code)
    values (%(channel_name)s, %(channel_type)s, %(recipient)s, %(remarks)s, %(user_code)s)
    returning channel_id
    """
    channel_id = db.insert(sql, data)
    logger.debug(f"{data['user_code']} | ALERT #{channel_id} inserted into database")
    return channel_id

def update_alert_channel(channel_id, data) -> int:
    data['channel_id'] = channel_id
    sql, _data = db.build_update_query(table_name='sc_alert_channel', data=data, primary_key_name='channel_id')
    r = db.update(sql, _data)
    logger.debug(f"ALERT #{channel_id} updated in database | {data}")
    return r

def delete_alert_channel(channel_id):
    sql = f"""delete from alert_channel where channel_id = {channel_id}"""
    r = db.query(sql)
    logger.debug(f"ALERT #{channel_id} deleted from database")
    return r
