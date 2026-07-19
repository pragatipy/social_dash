# scheduler/test_worker.py
from datetime import datetime, timedelta, timezone

from scheduler.engine import SchedulingEngine
from scheduler.models import ScheduledJob
from scheduler.worker import run_worker

engine = SchedulingEngine()

# Schedule a job due immediately
job = ScheduledJob(
    platform="x_tweet",
    account_id="user123",
    content={"content": "Testing the worker loop!", "hashtags": ["redis"]},
    scheduled_time=datetime.now(timezone.utc) - timedelta(seconds=1),
)
engine.schedule(job)
print("Scheduled job:", job.id)

# Run worker for a few iterations, poll every 3s
run_worker(engine, poll_interval=3, max_iterations=5)

# Check final state
final = engine.get_job(job.id)
print("\nFinal status:", final.status, "| retries:", final.retry_count)