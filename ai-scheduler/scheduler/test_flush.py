# scheduler/test_flush.py
from scheduler.engine import SchedulingEngine, DUE_INDEX_KEY

engine = SchedulingEngine()
keys = engine.r.keys("job:*")
if keys:
    engine.r.delete(*keys)
engine.r.delete(DUE_INDEX_KEY)
print(f"Flushed {len(keys)} job(s) and the due index.")