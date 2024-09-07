import os
import re
import json
import psycopg2
import socket
import logging
import threading
import pandas as pd
from contextlib import contextmanager

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

    def update(self, sql, f=()) -> int:
        with self.cursor_context(sql, f) as c:
            c.execute(sql, f)
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

            table_name = re.search("from \\w+", sql, re.IGNORECASE).group(0).split()[-1]
            if sql.startswith('delete'):
                self.logger.debug(f"{table_name} | Row deleted: {c.rowcount}")
            else:
                cols = list(map(lambda x: x[0], c.description))
                df = pd.DataFrame(c.fetchall(), columns=cols)
                if df.shape[0] > 0:
                    self.logger.debug(f"{table_name} | result size: (row x column) = {df.shape}")
                return df

    def commit(self):
        self.conn.commit()
        pass
