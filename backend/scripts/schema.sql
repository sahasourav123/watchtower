-- table to store monitors
CREATE TABLE monitors (
    monitor_id      SERIAL       PRIMARY KEY,
    org_id          INT          NOT NULL,
    user_code       TEXT         NOT NULL,
    monitor_name    TEXT         NOT NULL,
    monitor_type    TEXT         NOT NULL,
    monitor_body    JSONB        NOT NULL,
    is_active       boolean      DEFAULT TRUE,
    interval        INT          DEFAULT 300,
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

DROP MATERIALIZED VIEW IF EXISTS mv_uptime;

CREATE MATERIALIZED VIEW mv_uptime as
select * from vw_uptime;

REFRESH MATERIALIZED VIEW mv_uptime;

-- calculate daily (in minutes) uptime by date and monitor_id
-- create or replace view vw_uptime as
with history as (
    select *, date_trunc('day', created_at) as date,
           created_at - lag(created_at) over (partition by monitor_id order by created_at) as time_diff
    from run_history
--     order by created_at desc
), downtime as (
    select monitor_id, date, sum(extract(epoch from time_diff) / 60) as downtime_in_minutes
    from history
    where not outcome
    group by monitor_id, date
--     order by date desc
), moitor_agg as (
    select monitor_id, date, count(*) as check_count
    from history
    group by monitor_id, date
--     order by date desc
)
select m.monitor_id, m.monitor_name, moitor_agg.date as date, moitor_agg.check_count,
       coalesce(round(d.downtime_in_minutes, 2), 0) as downtime_in_minutes,
       round(100 * (1440 - coalesce(d.downtime_in_minutes, 0)) / 1440, 2) as uptime_pct
from moitor_agg
left join monitors m on m.monitor_id = moitor_agg.monitor_id
left join downtime d on d.monitor_id = moitor_agg.monitor_id and d.date = moitor_agg.date
order by date desc;

-- delete data older than 30 days
-- delete from run_history where created_at < now() - interval '30 days';