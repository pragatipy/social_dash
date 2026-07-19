# scheduler/test_redis_schedule.py
from datetime import datetime, timedelta, timezone

from scheduler.engine import SchedulingEngine
from scheduler.models import ScheduledJob

engine = SchedulingEngine()

job = ScheduledJob(
    platform="x_tweet",
    account_id="user123",
    content={"content": "Testing Redis persistence!", "hashtags": ["redis", "python"]},
    scheduled_time=datetime.now(timezone.utc) + timedelta(seconds=10),
)

engine.schedule(job)
print("Scheduled job with ID:", job.id)
print("Save this ID for the next script!")