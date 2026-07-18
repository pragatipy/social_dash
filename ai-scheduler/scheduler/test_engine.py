from datetime import datetime, timedelta, timezone

from scheduler.engine import SchedulingEngine
from scheduler.models import ScheduledJob
from scheduler.models import PostStatus

engine = SchedulingEngine()
job = ScheduledJob(
    platform="linkedin",
    account_id="user123",
    content={"text": "Hello LinkedIn!"},
    scheduled_time=datetime.now(timezone.utc) - timedelta(seconds=5),
)
engine.schedule(job)
for i in range(1, 6):
    job = engine.get_job(job.id)
    if job.status not in (PostStatus.SCHEDULED, PostStatus.RETRYING):
        print(f"Job no longer eligible for retry (status={job.status}), stopping.")
        break
    engine.mark_failed(job.id, f"simulated failure {i}")
    print(f"Attempt {i} -> Status: {job.status}, Retry Count: {job.retry_count}, Next: {job.next_attempt_time}")