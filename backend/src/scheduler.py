import os
import pytz
import logging
from typing import Literal
from utils.commons import logger
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from apscheduler.executors.pool import ThreadPoolExecutor
import controller as ct

class Scheduler:
    __instance = None
    scheduler = None

    def __new__(cls, *args, **kwargs):
        if not Scheduler.__instance:
            Scheduler.__instance = object.__new__(cls)

        return Scheduler.__instance

    def __init__(self):
        self.logger = logging.getLogger()
        pass

    def get_scheduler(self, max_instances=3, grace_time=10):

        # return scheduler if already exists
        if self.scheduler:
            return self.scheduler

        # create new scheduler
        tz = pytz.timezone('Asia/Kolkata')
        self.scheduler = BackgroundScheduler(timezone=tz)

        job_defaults = {
            'coalesce': True,
            'max_instances': max_instances,
            'misfire_grace_time': grace_time
        }

        job_stores = {
            'default': SQLAlchemyJobStore(
                url=f"postgresql://postgres:{os.getenv('TIMESCALEDB_PASS')}@{os.getenv('TIMESCALEDB_HOST')}:{os.getenv('TIMESCALEDB_PORT')}/postgres?application_name=scheduler",
                tablename="monitor_jobs"
            )
        }

        job_executors = {
            'default': ThreadPoolExecutor(3),
        }

        self.scheduler.configure(jobstores=job_stores, executors=job_executors, job_defaults=job_defaults)
        self.scheduler.start()
        return self.scheduler


scheduler = Scheduler().get_scheduler()

def create_job(monitor_id, interval: int, interval_unit: str, expiry: datetime, rerun: bool = True):
    job_id = f"monitor#{monitor_id}"
    _next_run_time = datetime.now() if rerun else None
    if interval_unit in ['s', 'seconds']:
        scheduler.add_job(ct.run_monitor_by_id, trigger='interval', args=[monitor_id], id=job_id, seconds=interval, replace_existing=True, jitter=30, next_run_time=_next_run_time, end_date=expiry)
    elif interval_unit in ['m', 'minutes']:
        scheduler.add_job(ct.run_monitor_by_id, trigger='interval', args=[monitor_id], id=job_id, minutes=interval, replace_existing=True, jitter=30, next_run_time=_next_run_time, end_date=expiry)
    elif interval_unit in ['h', 'hours']:
        scheduler.add_job(ct.run_monitor_by_id, trigger='interval', args=[monitor_id], id=job_id, hours=interval, replace_existing=True, jitter=30, next_run_time=_next_run_time, end_date=expiry)
    elif interval_unit in ['d', 'days']:
        scheduler.add_job(ct.run_monitor_by_id, trigger='interval', args=[monitor_id], id=job_id, days=interval, replace_existing=True, jitter=30, next_run_time=_next_run_time, end_date=expiry)
    elif interval_unit in ['w', 'weeks']:
        scheduler.add_job(ct.run_monitor_by_id, trigger='interval', args=[monitor_id], id=job_id, weeks=interval, replace_existing=True, jitter=30, next_run_time=_next_run_time, end_date=expiry)
    else:
        raise ValueError('Invalid Interval Unit')
    logger.info(f"{job_id} scheduled with interval {interval} sec")

def manage_job(action: Literal["pause", "resume", "delete"], monitor_id: int):
    job_id = f"monitor#{monitor_id}"
    # retrieve job if exists
    job = scheduler.get_job(job_id)
    if not job:
        logger.info(f"Job not found: {job_id}")
        return job_id

    match action.lower():
        case "pause":
            scheduler.pause_job(job_id)

        case "resume":
            scheduler.resume_job(job_id)

        case "remove":
            scheduler.remove_job(job_id)

    logger.info(f"Job Status Changed: {job_id} | {action}")
    return job_id
