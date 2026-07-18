import time
import random
from datetime import datetime, timezone

from scheduler.engine import SchedulingEngine
from scheduler.models import ScheduledJob


def publish_stub(job: ScheduledJob) -> None:
    """Placeholder for the real publish call.
    Members 2-4 own the actual platform API calls (LinkedIn/X/Meta).
    This stub simulates success/failure so we can test the worker loop
    end-to-end before that integration exists.
    Replace this with a real dispatch (e.g. an HTTP call to the backend,
    or direct import of platform publish functions) once available."""
    print(f"[publish_stub] Attempting to publish job {job.id} to {job.platform}...")
    time.sleep(1)  # simulate network latency
    if random.random() < 0.5:
        raise RuntimeError("Simulated platform API failure")
    print(f"[publish_stub] Successfully published job {job.id}")


def run_worker(engine: SchedulingEngine, poll_interval: int = 5, max_iterations: int | None = None):
    """Continuously polls for due jobs and attempts to publish them.

    poll_interval: seconds between checks
    max_iterations: if set, stop after N loop iterations (useful for testing;
                     leave as None to run forever, like a real worker would)
    """
    print(f"Worker started. Polling every {poll_interval}s. Press Ctrl+C to stop.")
    iterations = 0

    while True:
        due_jobs = engine.get_due_jobs()

        if due_jobs:
            print(f"\n[{datetime.now(timezone.utc).isoformat()}] Found {len(due_jobs)} due job(s)")

        for job in due_jobs:
            engine.mark_publishing(job.id)
            try:
                publish_stub(job)
                engine.mark_published(job.id)
            except Exception as e:
                updated = engine.mark_failed(job.id, str(e))
                print(f"[worker] Job {job.id} failed: {e} "
                      f"(status={updated.status}, retry_count={updated.retry_count}, "
                      f"next_attempt={updated.next_attempt_time})")

        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            print("Reached max_iterations, stopping.")
            break

        time.sleep(poll_interval)


if __name__ == "__main__":
    engine = SchedulingEngine()
    run_worker(engine, poll_interval=5)