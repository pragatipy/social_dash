from dotenv import load_dotenv
load_dotenv()

from typing import Optional, Union
from datetime import datetime


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_engine.generator import generate as ai_generate, refine as ai_refine
from scheduler.engine import SchedulingEngine
from scheduler.factory import draft_to_job, PlatformConstraintError
from scheduler.models import ScheduledJob

app = FastAPI(title="AI Content & Scheduler Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SchedulingEngine()


# ---- Request/response models ----

class GenerateRequest(BaseModel):
    platform: str          # "linkedin_post" | "linkedin_article" | "x_tweet" | "x_thread"
    topic: str
    tone: str = "professional"
    length: str = "medium"
    brand_voice: Optional[str] = None


class RefineRequest(BaseModel):
    platform: str
    draft: dict             # the previously generated draft, as JSON
    instruction: str


class ScheduleRequest(BaseModel):
    platform: str
    account_id: str
    draft: dict              # possibly user-edited content
    scheduled_time: datetime
    max_retries: int = 3


# ---- Endpoints ----

@app.post("/generate")
def generate_endpoint(req: GenerateRequest):
    try:
        draft = ai_generate(
            platform=req.platform,
            topic=req.topic,
            tone=req.tone,
            length=req.length,
            brand_voice=req.brand_voice,
        )
        return draft.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/refine")
def refine_endpoint(req: RefineRequest):
    # Reconstruct the right schema class from the platform, so refine()
    # can validate/rebuild the draft object before sending it back to the LLM
    from ai_engine.schemas import LinkedInPostDraft, LinkedInArticleDraft, XTweetDraft, XThreadDraft
    schema_map = {
        "linkedin_post": LinkedInPostDraft,
        "linkedin_article": LinkedInArticleDraft,
        "x_tweet": XTweetDraft,
        "x_thread": XThreadDraft,
    }
    schema_cls = schema_map.get(req.platform)
    if not schema_cls:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {req.platform}")

    draft_obj = schema_cls(**req.draft)
    refined = ai_refine(req.platform, draft_obj, req.instruction)
    return refined.model_dump()


@app.post("/schedule")
def schedule_endpoint(req: ScheduleRequest):
    try:
        job = draft_to_job(
            draft=req.draft,
            platform=req.platform,
            account_id=req.account_id,
            scheduled_time=req.scheduled_time,
            max_retries=req.max_retries,
        )
        engine.schedule(job)
        return {"job_id": job.id, "status": job.status.value}
    except PlatformConstraintError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/jobs/failed")
def get_failed_jobs_endpoint():
    failed = engine.get_failed_jobs()
    import json
    return [json.loads(j.to_json()) for j in failed]

@app.get("/jobs/{job_id}")
def get_job_endpoint(job_id: str):
    job = engine.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    data = job.to_json()
    import json
    return json.loads(data)


@app.get("/health")
def health():
    return {"status": "ok"}

