# scheduler/test_factory.py
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
load_dotenv()

from scheduler.factory import draft_to_job, PlatformConstraintError
from ai_engine.schemas import XTweetDraft  # adjust import path if yours differs

print("=" * 50)
print("Case 1: valid tweet -> should schedule fine")
good_tweet = XTweetDraft(
    content="Interns who ship real features learn 10x faster than interns stuck on toy projects.",
    hashtags=["internships", "softwareengineering"],
)
job = draft_to_job(
    draft=good_tweet,
    platform="x_tweet",
    account_id="user123",
    scheduled_time=datetime.now(timezone.utc) + timedelta(minutes=5),
)
print("Scheduled OK:", job.id, job.status)

print("=" * 50)
print("Case 2: user edits tweet to be too long -> should raise")
edited_tweet = good_tweet.model_dump()
edited_tweet["content"] = "x" * 300  # simulate a user override that's too long
try:
    draft_to_job(
        draft=edited_tweet,
        platform="x_tweet",
        account_id="user123",
        scheduled_time=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    print("ERROR: should have raised but didn't!")
except PlatformConstraintError as e:
    print("Correctly raised PlatformConstraintError:", e)

print("=" * 50)
print("Case 3: fixed-length edit -> should schedule fine")
edited_tweet["content"] = "Fixed and short now."
job2 = draft_to_job(
    draft=edited_tweet,
    platform="x_tweet",
    account_id="user123",
    scheduled_time=datetime.now(timezone.utc) + timedelta(minutes=5),
)
print("Scheduled OK:", job2.id, job2.status)