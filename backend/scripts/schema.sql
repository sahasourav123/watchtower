-- table to store monitors
CREATE TABLE monitors (
    monitor_id      SERIAL       PRIMARY KEY,
    monitor_name    TEXT         NOT NULL,
    monitor_type    TEXT         NOT NULL,
    monitor_body    JSONB        NOT NULL,
    is_active       boolean      DEFAULT TRUE,
    frequency       INT          DEFAULT 300,
    timeout         INT          DEFAULT 5,
    expectation     JSONB,
    alerts          TEXT[],
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
