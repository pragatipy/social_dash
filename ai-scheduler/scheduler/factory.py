from datetime import datetime
from typing import Union

from pydantic import BaseModel

from scheduler.models import ScheduledJob


class PlatformConstraintError(Exception):
    """Raised when content violates a hard platform limit (not an AI style preference)."""


def _check_platform_constraints(content: dict, platform: str) -> None:
    if platform == "x_tweet":
        text = content.get("content", "")
        if len(text) > 280:
            raise PlatformConstraintError(f"Tweet is {len(text)} chars, exceeds X's 280 limit")
    elif platform == "x_thread":
        for i, tweet in enumerate(content.get("tweets", [])):
            if len(tweet) > 280:
                raise PlatformConstraintError(f"Tweet {i+1} is {len(tweet)} chars, exceeds X's 280 limit")


def draft_to_job(
    draft: Union[BaseModel, dict],
    platform: str,
    account_id: str,
    scheduled_time: datetime,
    max_retries: int = 3,
) -> ScheduledJob:
    """Convert a (possibly user-edited) draft into a schedulable job.
    Accepts the content as final/approved — does not re-run AI-side style
    validation (hashtags, tone) — but still checks hard platform limits
    the target API would reject outright."""
    content = draft.model_dump() if isinstance(draft, BaseModel) else draft
    _check_platform_constraints(content, platform)

    return ScheduledJob(
        platform=platform,
        account_id=account_id,
        content=content,
        scheduled_time=scheduled_time,
        max_retries=max_retries,
    )