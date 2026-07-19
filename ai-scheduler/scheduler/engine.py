from datetime import datetime, timedelta, timezone
from typing import List, Optional

import redis

from scheduler.models import ScheduledJob, PostStatus

DUE_INDEX_KEY = "jobs:due_index"
FAILED_INDEX_KEY = "jobs:failed_index"

def _job_key(job_id: str) -> str:
    return f"job:{job_id}"


class SchedulingEngine:
    """Redis-backed scheduling engine.
    - job:<id>        -> JSON-serialized ScheduledJob (the record)
    - jobs:due_index   -> sorted set, score = next_attempt_time (unix ts), member = job id
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.r = redis_client or redis.Redis(host="localhost", port=6379, decode_responses=True)

    def schedule(self, job: ScheduledJob) -> ScheduledJob:
        job.next_attempt_time = job.scheduled_time
        self.r.set(_job_key(job.id), job.to_json())
        self.r.zadd(DUE_INDEX_KEY, {job.id: job.next_attempt_time.timestamp()})
        return job

    def get_due_jobs(self, now: Optional[datetime] = None) -> List[ScheduledJob]:
        now = now or datetime.now(timezone.utc)
        due_ids = self.r.zrangebyscore(DUE_INDEX_KEY, min=0, max=now.timestamp())
        jobs = []
        for job_id in due_ids:
            raw = self.r.get(_job_key(job_id))
            if raw:
                jobs.append(ScheduledJob.from_json(raw))
        return jobs

    def _save(self, job: ScheduledJob) -> None:
        self.r.set(_job_key(job.id), job.to_json())

    def mark_publishing(self, job_id: str) -> ScheduledJob:
        job = self.get_job(job_id)
        job.status = PostStatus.PUBLISHING
        job.updated_at = datetime.now(timezone.utc)
        self._save(job)
        self.r.zrem(DUE_INDEX_KEY, job_id)  # no longer "due" while actively publishing
        return job

    def mark_published(self, job_id: str) -> ScheduledJob:
        job = self.get_job(job_id)
        job.status = PostStatus.PUBLISHED
        job.updated_at = datetime.now(timezone.utc)
        self._save(job)
        self.r.zrem(DUE_INDEX_KEY, job_id)
        return job

    def mark_failed(self, job_id: str, error: str) -> ScheduledJob:
        job = self.get_job(job_id)
        job.last_error = error
        job.retry_count += 1
        job.updated_at = datetime.now(timezone.utc)

        if job.retry_count > job.max_retries:
            job.status = PostStatus.FAILED
            job.next_attempt_time = None
            self._save(job)
            self.r.zrem(DUE_INDEX_KEY, job_id)
            self.r.sadd(FAILED_INDEX_KEY, job_id)
        else:
            job.status = PostStatus.RETRYING
            backoff_seconds = 60 * (2 ** (job.retry_count - 1))
            job.next_attempt_time = datetime.now(timezone.utc) + timedelta(seconds=backoff_seconds)
            self._save(job)
            self.r.zadd(DUE_INDEX_KEY, {job_id: job.next_attempt_time.timestamp()})

        return job

    def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        raw = self.r.get(_job_key(job_id))
        return ScheduledJob.from_json(raw) if raw else None
    

    def get_failed_jobs(self) -> List[ScheduledJob]:
        failed_ids = self.r.smembers(FAILED_INDEX_KEY)
        jobs = []
        for job_id in failed_ids:
            raw = self.r.get(_job_key(job_id))
            if raw:
                jobs.append(ScheduledJob.from_json(raw))
        return jobs