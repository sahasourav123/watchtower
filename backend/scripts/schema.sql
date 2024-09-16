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
    org_id          INT          NOT NULL,
    monitor_id      INT          NOT NULL,
    outcome         boolean      NOT NULL,
    response_time   INT          NOT NULL,
    response        text,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
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