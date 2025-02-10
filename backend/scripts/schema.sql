-- table to store monitors
CREATE TABLE monitors (
    monitor_id      SERIAL       PRIMARY KEY,
    org_id          INT          NOT NULL,
    user_code       TEXT         NOT NULL,
    monitor_group   text,
    monitor_name    TEXT         NOT NULL,
    monitor_type    TEXT         NOT NULL,
    monitor_body    JSONB        NOT NULL,
    is_active       boolean      DEFAULT TRUE,
    interval        INT          DEFAULT 10,
    interval_unit   TEXT         DEFAULT 'minutes',
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
    recipient           JSONB        NOT NULL,
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

-- ============================================
-- Hypertable
-- ============================================
SELECT create_hypertable('run_history', 'created_at', migrate_data => true);

-- create additional Index
CREATE INDEX run_history_monitor_id_created_at_index on run_history (monitor_id, created_at);

-- create Retention Policy
select remove_retention_policy('run_history');
SELECT add_retention_policy('run_history', INTERVAL '3 days');


-- ============================================
-- materialized view for uptime history
-- ============================================
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


-- calculate daily (in minutes) uptime by date and monitor_id
drop view if exists vw_uptime_summary;
create or replace view vw_uptime_summary as
with agg_stats as (
    select monitor_id, date(date) as date,
        round((success::numeric/total)*100, 2) as uptime_pct,
        round(((fail_count/total) * extract(epoch from total_check_time) / 60), 2) as downtime_in_minutes,
        fail_count,
        total,
        avg_rt, p90_rt
    from mv_uptime
)
select m.monitor_group, m.monitor_name, m.monitor_type, agg_stats.*
from agg_stats
left join monitors m on m.monitor_id = agg_stats.monitor_id;


-- ============================================
-- materialized view for daily stats
-- ============================================
DROP MATERIALIZED VIEW IF EXISTS mv_stats;

CREATE MATERIALIZED VIEW mv_stats
WITH (timescaledb.continuous) AS
select monitor_id, response, outcome as is_success,
       time_bucket('1 day', created_at) AS date,
       count(*) as total,
      max(created_at) last_check_time
from run_history
group by monitor_id, outcome, response, date;

select remove_continuous_aggregate_policy('mv_stats');

SELECT add_continuous_aggregate_policy('mv_stats',
    start_offset => INTERVAL '1 day',
    end_offset => NULL,
    schedule_interval => INTERVAL '1 minute'
);

drop view if exists vw_daily_stats;
create or replace view vw_daily_stats as
with agg_stats as (
    select monitor_id,
        response, is_success,
        sum(total) as total_count,
        max(last_check_time) as last_check_time
    from mv_stats
    group by monitor_id, is_success, response
)
select m.monitor_group, m.monitor_name, m.monitor_type, m.user_code, agg_stats.*
from agg_stats
right join monitors m on m.monitor_id = agg_stats.monitor_id
order by monitor_id, is_success, last_check_time desc;


-- ============================================
-- Queries
-- ============================================
-- last 90 days check count
select date(date) as date, sum(total) as total_count
from mv_uptime
where date >= current_date - interval '90 day'
group by date
order by date;

-- total checks till date
select sum(total) as total_checks from mv_uptime;

--
select * from vw_daily_stats;
select * from vw_uptime_summary;