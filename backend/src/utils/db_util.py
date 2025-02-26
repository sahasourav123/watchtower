import os
import re
import json
import psycopg2
import socket
import logging
import threading
import pandas as pd
from contextlib import contextmanager

import redis

class RedisManager:

    def __init__(self):
        self.conn = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'), decode_responses=True)

    # ===========================================
    # common methods
    # ===========================================
    def set(self, key, value, ttl=None):
        self.conn.set(key, json.dumps(value), ex=ttl)

    def get(self, key: str, expected_type=str):
        val = self.conn.get(key)
        if expected_type == str or not val:
            return val

        elif expected_type == bool:
            return val == 'True'

        if expected_type in [dict, list]:
            return json.loads(val)

        elif expected_type == int:
            return int(val)

    def delete(self, key):
        res = self.conn.delete(key)
        return res == 1

    # ===========================================
    # functionality specific methods
    # ===========================================
    # Example Usage: to search all token for a given user_code
    def search_keys(self, pattern: str):
        return self.conn.keys(pattern)

    # Example Usage: get value for given api token
    def get_value_by_key_pattern(self, pattern: str):
        keys = self.conn.scan(match=pattern)[1]
        if len(keys) > 0:
            return self.conn.get(keys[0])

    def expiring_counter(self, key: str, ttl=60):
        _key = f"rate-limit#{key}"
        if not self.conn.exists(_key):
            self.conn.set(_key, 1, ex=ttl)
            return 1
        else:
            return self.conn.incr(_key)


class DatabaseManager:

    def __init__(self):
        self.lock = threading.Lock()
        self.logger = logging.getLogger()
        self.conn = self._get_connection()

    def _pre_process(self, data: dict) -> dict:
        for k, v in data.items():
            if isinstance(v, dict):
                data[k] = json.dumps(v)
        return data

    def _get_connection(self):
        try:
            _this_ = f"wt-{os.getenv('ENV')}-{socket.gethostname()}"
            conn_str = f"dbname=postgres user=postgres password={os.getenv('TIMESCALEDB_PASS')} host={os.getenv('TIMESCALEDB_HOST')} port={os.getenv('TIMESCALEDB_PORT')} application_name={_this_}"
            conn = psycopg2.connect(conn_str)
            self.logger.info(f'database connection created...')
            return conn

        except Exception as e:
            self.logger.exception(f'database connection failed | {e.args[0]}')
            raise e

    # context handler for exception handle and cursor closing
    @contextmanager
    def cursor_context(self, query, data):
        self.lock.acquire(True)
        sql = " ".join(query.split())

        # Get cursor
        try:
            c = self.conn.cursor()
        except Exception as e:
            self.conn = self._get_connection()
            c = self.conn.cursor()

        # query execution
        try:
            yield c
        except Exception as e:
            self.logger.error("Database operation failed: \n {}".format(e))
            c.execute('ROLLBACK')
            raise Exception('Database operation failed on SQL: {} >>> Data: {} >>> Exception: {}'.format(sql, data, str(e)))

        finally:
            # self.logger.debug(f"Query Executed: {sql}")
            c.close()
            self.lock.release()

    def insert(self, sql: str, data: tuple | dict = ()) -> int:
        _data = self._pre_process(data) if isinstance(data, dict) else data
        with self.cursor_context(sql, _data) as c:
            c.execute(sql, _data)
            self.commit()
            try: return c.fetchone()[0]
            except: return None

    def insert_many(self, sql: str, f: dict | list[tuple]):
        with self.cursor_context(sql, f) as c:
            c.executemany(sql, f)
            self.commit()
            return c.rowcount

    def update(self, sql, data=()) -> int:
        _data = self._pre_process(data) if isinstance(data, dict) else data
        with self.cursor_context(sql, _data) as c:
            c.execute(sql, _data)
            self.commit()
            return c.rowcount

    # update many records
    def update_many(self, sql, f, do_commit=True) -> int:
        with self.cursor_context(sql, f) as c:
            c.executemany(sql, f)
            if do_commit:
                self.commit()
            return c.rowcount

    def query(self, sql, f=()) -> pd.DataFrame:
        with self.cursor_context(sql, f) as c:
            c.execute(sql, f)
            self.commit()

            cols = list(map(lambda x: x[0], c.description))
            df = pd.DataFrame(c.fetchall(), columns=cols)
            return df

    def delete(self, sql, f=()) -> int:
        with self.cursor_context(sql, f) as c:
            c.execute(sql, f)
            self.commit()
            return c.rowcount

    def commit(self):
        self.conn.commit()
        pass

