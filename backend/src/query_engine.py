import pandas as pd

from utils.commons import logger
from utils.db_util import DatabaseManager

db = DatabaseManager()

def monitor_stats(user_code: str = None):
    sql = f"""
    select monitor_type,
        count(*) as total_monitors,
        sum(is_active::int) as active_monitors
    from monitors
    {f"where user_code = '{user_code}'" if user_code else ""}
    group by monitor_type
    """
    return db.query(sql)

def daywise_execution_stats(day_limit: int = 90):
    sql = f"""
    select date(date) as date, sum(total) as total_count
    from mv_uptime
    where date >= current_date - interval '{day_limit} day'
    group by date
    order by date
    """
    return db.query(sql)

def final_execution_stats():
    sql = f"""select monitor_type, sum(total) as total_checks 
    from vw_uptime_summary
    group by monitor_type
    """
    return db.query(sql)

def response_stats(user_code: str = None):
    sql = f"""select * from vw_daily_stats
    {f"where user_code = '{user_code}'" if user_code else ""}
    """
    return db.query(sql)


def _builder(filters: dict):
    clause_list = []
    for k, v in filters.items():
        if not v:
            continue
        elif k in ['monitor_body', 'expectation', 'alerts', 'tags']:
            clause_list.append(f"{k} @> %({k})s")
        elif isinstance(v, list):
            clause_list.append(f"{k} in {tuple(v)}")
        else:
            clause_list.append(f"{k}=%({k})s")

    return ' and '.join(clause_list)

def get_monitors(filters):
    sql = "select * from monitors"
    if filters:
        sql = f"{sql} where {_builder(filters)}"

    sql = f"{sql} order by monitor_group, monitor_type"
    return db.query(sql, filters)

def get_monitor_by_id(monitor_id: int):
    sql = f"select * from monitors where monitor_id={monitor_id}"
    _df = db.query(sql)
    monitor = _df.to_dict('records')[0]
    return monitor

def insert_monitor(data: dict):
    logger.info(f"Creating monitor: {data}")
    sql = """insert into monitors (monitor_type, monitor_name, monitor_body, timeout, interval, interval_unit, expiry, expectation, alerts, user_code, monitor_group, tags)
    values (%(monitor_type)s, %(monitor_name)s, %(monitor_body)s, %(timeout)s, %(interval)s, %(interval_unit)s, %(expiry)s,  %(expectation)s, %(alerts)s, %(user_code)s, %(monitor_group)s, %(tags)s)
    returning monitor_id
    """
    monitor_id = db.insert(sql, data)
    logger.info(f"Inserted Monitor with id {monitor_id}")
    return monitor_id

def update_monitor(user_code: str, monitor_id: int, data: dict) -> int:
    logger.info(f"Updating monitor: {data}")
    sql = f"""
        UPDATE monitors SET
            {','.join([f"{key}=%({key})s" for key in data.keys()])}
        WHERE monitor_id = {monitor_id} and user_code = '{user_code}'
        """
    r = db.update(sql, data)
    logger.info(f"Updated Monitor with id {monitor_id}")
    return r

def delete_monitor(user_code: str, monitor_id: int):
    logger.info(f"Deleting monitor: #{monitor_id}")
    sql = f"delete from monitors where monitor_id = {monitor_id} and user_code = '{user_code}'"
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

def fetch_recent_history_by_user(filters: dict, limit: int = 10):
    sql = f"""
    WITH ranked_history AS (
        SELECT monitor_id, outcome, response_time, ROW_NUMBER() OVER (PARTITION BY monitor_id ORDER BY created_at DESC) AS rn
        FROM run_history
        where monitor_id in (
            select monitor_id from monitors 
            where {_builder(filters)}
        )
    )
    SELECT monitor_id, array_agg(outcome) AS outcomes, array_agg(response_time) as response_times
    FROM ranked_history
    WHERE rn <= {limit}
    group by monitor_id
    """
    return db.query(sql, filters)

def daily_uptime_history(filters: dict, day_limit: int):
    sql = f"""
    select * 
    from vw_uptime_summary 
    where monitor_id in (
        select monitor_id from monitors 
        where {_builder(filters)}
    )
    and date >= current_date - interval '{day_limit} days'
    order by date, monitor_id
    """
    return db.query(sql, filters)

def insert_monitor_history(monitor_id: int, outcome: bool, response_code: int, response_time_ms: int):
    # store run history
    sql = f"""insert into run_history (monitor_id, outcome, response_time, response, created_at) 
    values ({monitor_id}, {outcome}, {response_time_ms or 0}, {response_code}, current_timestamp)
    """
    db.insert(sql)


"""
================================================
ALERT CHANNEL
================================================
"""
def get_alert_channel(filters: dict) -> pd.DataFrame:
    sql = f"select * from alert_channel where {_builder(filters)}"
    return db.query(sql, filters)

def insert_alert_channel(data) -> int:
    sql = """insert into alert_channel (channel_name, channel_type, recipient, remarks, user_code)
    values (%(channel_name)s, %(channel_type)s, %(recipient)s, %(remarks)s, %(user_code)s)
    returning channel_id
    """
    channel_id = db.insert(sql, data)
    logger.debug(f"{data['user_code']} | ALERT #{channel_id} inserted into database")
    return channel_id

def delete_alert_channel(channel_id):
    sql = f"""delete from alert_channel where channel_id = {channel_id}"""
    r = db.query(sql)
    logger.debug(f"ALERT #{channel_id} deleted from database")
    return r
