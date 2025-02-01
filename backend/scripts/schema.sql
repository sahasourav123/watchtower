-- table to store monitors
CREATE TABLE monitors (
    monitor_id      SERIAL       PRIMARY KEY,
    org_id          INT          NOT NULL,
    user_code       TEXT         NOT NULL,
    monitor_name    TEXT         NOT NULL,
    monitor_type    TEXT         NOT NULL,
    monitor_body    JSONB        NOT NULL,
    is_active       boolean      DEFAULT TRUE,
    interval        INT          DEFAULT 5,
    interval_unit   TEXT         DEFAULT 'm',
    expiry          date,
    timeout         INT          DEFAULT 5,
    expectation     JSONB,
    alerts          TEXT[],
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- monitor run history
create table run_history (
    run_id          SERIAL       PRIMARY KEY,
    monitor_id      INT          NOT NULL,
    outcome         boolean      NOT NULL,
    response_time   INT          NOT NULL,
    response        text,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- alert channel
CREATE TABLE IF NOT EXISTS ALERT_CHANNEL (
    CHANNEL_ID          SERIAL      PRIMARY KEY,
    CHANNEL_NAME        TEXT,
    CHANNEL_TYPE        TEXT,
    CHANNEL_BODY        TEXT,
    IS_ACTIVE           BOOL DEFAULT true,      -- true / false
    REMARKS             TEXT,
    USER_CODE           TEXT,
    org_id              INT,
    created_at          TIMESTAMP DEFAULT now()
);


select * from monitors;

-- select last 10 record of each monitor_id from run_history table
WITH ranked_history AS (
    SELECT monitor_id, outcome, ROW_NUMBER() OVER (PARTITION BY monitor_id ORDER BY created_at DESC) AS rn
    FROM run_history
)
SELECT monitor_id, string_agg(outcome::text, ' ') AS outcomes
FROM ranked_history
WHERE rn <= 10
group by monitor_id;

-- calculate time diff between two consecutive timestamp for each monitor_id
select *, created_at - lag(created_at) over (partition by monitor_id order by created_at) as time_diff
from run_history
order by created_at;


SELECT create_hypertable('run_history', 'created_at', migrate_data => true);

-- create additional Index
CREATE INDEX run_history_monitor_id_created_at_index on run_history (monitor_id, created_at);

-- create Retention Policy
select remove_retention_policy('run_history');
SELECT add_retention_policy('run_history', INTERVAL '3 days');

DROP MATERIALIZED VIEW IF EXISTS mv_uptime;

CREATE MATERIALIZED VIEW mv_uptime
WITH (timescaledb.continuous) AS
select monitor_id,
       time_bucket('1 day', created_at) AS date,
--        date_trunc('day', created_at) as date,
       count(*) as total,
       sum(case when outcome = true then 1 else 0 end)::numeric as success,
       round(avg(response_time)::numeric, 2) as avg_rt,
       -- 90 % response time
       round((percentile_cont(0.9) within group (order by response_time))::numeric, 2) as p90_rt,
      sum(case when outcome = false then 1 else 0 end)::numeric as fail_count,
      -- total check time
      max(created_at) - min(created_at) total_check_time
from run_history
group by monitor_id, date;

select remove_continuous_aggregate_policy('mv_uptime');

SELECT add_continuous_aggregate_policy('mv_uptime',
    start_offset => INTERVAL '1 day',
    end_offset => NULL,
    schedule_interval => INTERVAL '1 minute'
);

select * from mv_uptime
order by date desc;


-- calculate daily (in minutes) uptime by date and monitor_id
create or replace view vw_uptime_summary as
with agg_stats as (
    select monitor_id, date(date) as date,
        round((success::numeric/total)*100, 2) as uptime_pct,
        round(((fail_count/total) * extract(epoch from total_check_time) / 60), 2) as downtime_in_minutes,
        fail_count,
        avg_rt, p90_rt
    from mv_uptime
)
select agg_stats.*, m.monitor_name
from agg_stats
left join monitors m on m.monitor_id = agg_stats.monitor_id;

--order by date desc, monitor_id;

-- delete data older than 30 days
-- delete from run_history where created_at < now() - interval '30 days';