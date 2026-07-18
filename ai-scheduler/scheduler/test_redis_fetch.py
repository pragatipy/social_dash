# scheduler/test_redis_fetch.py
import sys

from scheduler.engine import SchedulingEngine

if len(sys.argv) < 2:
    print("Usage: python -m scheduler.test_redis_fetch <job_id>")
    sys.exit(1)

job_id = sys.argv[1]

engine = SchedulingEngine()
job = engine.get_job(job_id)

if job is None:
    print("Job not found! Persistence failed.")
else:
    print("Found job! Persistence works.")
    print(job)

due = engine.get_due_jobs()
print("Due jobs right now:", [j.id for j in due])