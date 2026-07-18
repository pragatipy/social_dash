import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


class PostStatus(str, Enum):
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class ScheduledJob:
    platform: str
    account_id: str
    content: dict
    scheduled_time: datetime

    id: str = field(default_factory=lambda: str(uuid4()))
    status: PostStatus = PostStatus.SCHEDULED
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    next_attempt_time: Optional[datetime] = None

    def to_json(self) -> str:
        data = asdict(self)
        data["status"] = self.status.value
        for key in ("scheduled_time", "created_at", "updated_at", "next_attempt_time"):
            if data[key] is not None:
                data[key] = data[key].isoformat()
        return json.dumps(data)

    @classmethod
    def from_json(cls, raw: str) -> "ScheduledJob":
        data = json.loads(raw)
        data["status"] = PostStatus(data["status"])
        for key in ("scheduled_time", "created_at", "updated_at", "next_attempt_time"):
            if data[key] is not None:
                data[key] = datetime.fromisoformat(data[key])
        return cls(**data)