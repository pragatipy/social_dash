# AI Content Generator & Scheduler (Member 5)
 
Handles AI-powered content generation (LinkedIn/X) and post scheduling with retry logic, backed by Redis for persistence.
 
## Setup
 
1. Install dependencies:
```
   uv sync
```
 
2. Create a `.env` file in this folder with:
```
   GOOGLE_API_KEY=your_gemini_api_key_here
```
 
3. Start Redis (requires Docker):
```
   docker run -d --name redis-scheduler -p 6379:6379 redis:latest
```
 
4. Start the API server:
```
   uv run uvicorn main:app --reload --port 8000
```
 
5. Explore/test endpoints interactively at `http://localhost:8000/docs`
## Running the worker
 
The scheduler engine stores jobs in Redis, but something needs to continuously check for due jobs and attempt to publish them. Run this in a separate terminal:
 
```
python -m scheduler.worker
```
 
**Known limitation:** this currently must be started manually and left running. In a real deployment this would need to run as a persistent background process (e.g. a system service, or a `pm2`/`systemd`-managed process) — not yet set up for production.
 
**Note:** the worker currently calls `publish_stub()` in `scheduler/worker.py`, which randomly simulates success/failure. This needs to be replaced with real calls into the LinkedIn/X/Meta publish logic (Members 2-4) once available.
 
## API Endpoints
 
### `POST /generate`
Generate a content draft.
 
Request:
```json
{
  "platform": "linkedin_post",
  "topic": "string",
  "tone": "professional",
  "length": "medium",
  "brand_voice": "optional string describing brand/personal voice"
}
```
- `platform`: `linkedin_post` | `linkedin_article` | `x_tweet` | `x_thread`
- `tone`: `professional` | `casual` | `bold` | `storytelling`
- `length`: `short` | `medium` | `long`
Response: the generated draft (shape varies by platform — see `ai_engine/schemas.py`), e.g.:
```json
{ "content": "...", "hashtags": ["...", "..."] }
```
 
### `POST /refine`
Refine an existing draft based on an instruction (e.g. "make it shorter").
 
Request:
```json
{
  "platform": "linkedin_post",
  "draft": { "content": "...", "hashtags": ["..."] },
  "instruction": "make it more casual"
}
```
 
Response: the refined draft, same shape as `/generate`.
 
### `POST /schedule`
Schedule a (possibly user-edited) draft to be published at a specific time.
 
Request:
```json
{
  "platform": "x_tweet",
  "account_id": "string",
  "draft": { "content": "...", "hashtags": ["..."] },
  "scheduled_time": "2026-07-18T15:00:00Z",
  "max_retries": 3
}
```
 
Response:
```json
{ "job_id": "uuid", "status": "scheduled" }
```
 
Note: hard platform constraints (e.g. X's 280-char limit) are enforced here even on user-edited content, and will return a `422` error if violated. AI-style formatting (hashtag symbols, tone) is NOT re-validated after user edits — user-approved content is treated as final.
 
### `GET /jobs/{job_id}`
Fetch the current status/details of a specific job.
 
### `GET /jobs/failed`
List all jobs that have permanently failed (exceeded `max_retries`). Intended to power failure notifications in the frontend.
 
### `GET /health`
Basic health check.
 
## Job status lifecycle
 
```
scheduled → publishing → published
                ↓
             failed → retrying → publishing (loop, up to max_retries)
                ↓ (retries exhausted)
             failed (permanent)
```
 
Retry backoff is exponential: 60s, 120s, 240s, ...
 
## Architecture notes
 
- **AI generation** (`ai_engine/`): LangChain + Gemini, structured output via Pydantic schemas — no LangGraph currently, kept simple as one chain per platform/format.
- **Scheduling** (`scheduler/`): a hand-built state machine (not BullMQ/Celery) persisted in Redis:
  - `job:<id>` — a JSON-serialized `ScheduledJob` record
  - `jobs:due_index` — a Redis sorted set (score = next attempt time as a Unix timestamp) used to efficiently find due jobs
  - `jobs:failed_index` — a Redis set of permanently failed job IDs
- **API layer** (`main.py`): FastAPI, CORS-enabled for `http://localhost:3000` (Next.js dev server).
- This service is intentionally self-contained — it doesn't call LinkedIn/X/Meta APIs directly. Members 2-4 own the actual platform publish calls; the worker's `publish_stub()` is the integration point to replace once that code exists.