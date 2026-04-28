# AI Resume Tailor (MVP)

AI Resume Tailor is a production-style MVP that compares a resume to a job
description and returns structured, actionable recommendations.

- Frontend: React + Next.js + Tailwind
- Backend: FastAPI + OpenAI

---

## Why this architecture

### 1) Clear separation of concerns
- The backend owns business logic, validation, safety constraints, and LLM calls.
- The frontend owns user interaction, rendering states, and copy/export UX.
- This keeps both layers simpler to evolve independently.

### 2) API-first contract
- `POST /analyze` is defined with strict Pydantic models.
- Frontend and backend both use the same response shape conceptually.
- This minimizes integration drift and prevents loosely formatted AI outputs.

### 3) Production-friendly defaults
- Backend includes input validation, error mapping, and observability logs.
- LLM output is parsed as JSON and validated before returning to clients.
- Preprocessing reduces token waste while preserving evidence fidelity.

### 4) Fast iteration path
- Next.js gives a scalable React app structure from day one.
- FastAPI keeps backend iteration quick with strong typing and auto docs.
- Folder structure is intentionally modular so each area can grow without refactors.

---

## Folder structure (what and why)

```text
AIResumeTailor/
  README.md
  backend/
    .env
    main.py
    prompts.py
    schemas.py
    requirements.txt
    services/
      __init__.py
      llm.py
  frontend/
    package.json
    tsconfig.json
    next.config.ts
    tailwind.config.ts
    postcss.config.js
    eslint.config.mjs
    src/
      app/
        layout.tsx
        globals.css
        page.tsx
      components/
        copy-button.tsx
      lib/
        api.ts
```

### Root
- `README.md`: project-level documentation, setup, architecture rationale, and API contract.

### `backend/`
Contains all server-side logic. It is separated so Python dependencies and runtime are isolated from frontend tooling.

### `frontend/`
Contains all UI/client logic. It is separated so React/Node ecosystem tooling remains independent from Python backend.

---

## File-by-file explanation (what + why)

## Backend

### `backend/main.py`
**What it does**
- Creates the FastAPI app.
- Configures CORS for local frontend origin.
- Exposes:
  - `GET /health`
  - `POST /analyze`
- Logs request lifecycle events with `request_id`.
- Converts internal LLM/service exceptions to HTTP errors.

**Why it is needed**
- This is the backend entry point and API router.
- Keeps transport-layer responsibilities (HTTP, CORS, status codes, request logging) in one place.
- Prevents business logic from leaking into route handlers.

### `backend/schemas.py`
**What it does**
- Defines request model: `AnalyzeRequest`.
- Defines response model: `AnalyzeResponse`.
- Enforces:
  - min input length
  - `match_score` range `0-100`
  - cleaned list items (no blank entries)

**Why it is needed**
- Ensures all API inputs/outputs stay contract-safe.
- Guards against malformed user payloads and malformed LLM output.
- Makes backend behavior predictable for the frontend.

### `backend/prompts.py`
**What it does**
- Stores compact `SYSTEM_PROMPT` rules.
- Builds task prompt via `build_user_prompt(resume_text, jd_text)`.
- Enforces JSON-only output format in prompt instructions.

**Why it is needed**
- Centralizes prompt logic to avoid string duplication.
- Makes prompt tuning easy without touching service or route code.
- Keeps prompts token-efficient and model-friendly.

### `backend/services/llm.py`
**What it does**
- Loads LLM config from env.
- Preprocesses resume text conservatively:
  - normalize line endings
  - remove obvious noise lines
  - deduplicate exact repeated lines
  - collapse blank-line runs
  - cap extreme length
  - fallback to near-original if cleanup is too aggressive
- Calls OpenAI chat completion with JSON response format.
- Parses JSON and validates against `AnalyzeResponse`.
- Emits observability logs (length/stats only, no raw content).

**Why it is needed**
- Isolates all model/provider logic from API routes.
- Improves reliability and safety around AI output handling.
- Controls token usage without sacrificing evidence integrity.

### `backend/services/__init__.py`
**What it does**
- Marks `services` as a Python package.

**Why it is needed**
- Enables clean imports such as `from services.llm import ...`.

### `backend/requirements.txt`
**What it does**
- Lists Python runtime dependencies (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `openai`).

**Why it is needed**
- Reproducible backend environment setup across machines.

### `backend/.env`
**What it does**
- Holds runtime configuration:
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`
  - preprocessing limits
  - logging flags

**Why it is needed**
- Keeps secrets and deploy-time config out of code.
- Supports environment-specific behavior without code edits.

## Frontend

### `frontend/package.json`
**What it does**
- Defines frontend scripts (`dev`, `build`, `start`, `lint`) and dependencies.

**Why it is needed**
- Standard Node project manifest for dependency + script management.

### `frontend/tsconfig.json`
**What it does**
- Configures TypeScript compiler behavior and path aliases (`@/*`).

**Why it is needed**
- Type safety and maintainable imports across growing UI code.

### `frontend/next.config.ts`
**What it does**
- Defines Next.js runtime/build configuration.

**Why it is needed**
- Provides a centralized place for future frontend runtime tuning.

### `frontend/tailwind.config.ts`
**What it does**
- Configures Tailwind content scanning and theme extensions.

**Why it is needed**
- Enables utility-first styling and consistent design tokens.

### `frontend/postcss.config.js`
**What it does**
- Wires PostCSS plugins (Tailwind + autoprefixer).

**Why it is needed**
- Required build pipeline for Tailwind CSS processing.

### `frontend/eslint.config.mjs`
**What it does**
- Sets linting rules for Next.js + TypeScript.

**Why it is needed**
- Catches code quality and correctness issues early.

### `frontend/src/app/layout.tsx`
**What it does**
- Provides root layout and metadata for App Router pages.

**Why it is needed**
- Shared shell and page metadata should not be duplicated per page.

### `frontend/src/app/globals.css`
**What it does**
- Imports Tailwind layers and global base styles.

**Why it is needed**
- Single place for global visual defaults.

### `frontend/src/app/page.tsx`
**What it does**
- Implements the main product flow:
  - two textareas
  - analyze button + spinner
  - error state
  - score and recommendation sections
  - responsive layout

**Why it is needed**
- It is the primary user-facing workflow for the MVP.

### `frontend/src/lib/api.ts`
**What it does**
- Exposes typed `analyzeResume()` API call to backend.
- Handles non-200 errors in one place.

**Why it is needed**
- Avoids fetch logic duplication inside UI components.
- Keeps networking concerns separated from rendering logic.

### `frontend/src/components/copy-button.tsx`
**What it does**
- Reusable copy-to-clipboard action with temporary feedback.

**Why it is needed**
- Improves UX and prevents repeating copy logic for each result section.

---

## Request flow (end-to-end)

1. User enters resume + JD in frontend.
2. Frontend calls backend `POST /analyze`.
3. Backend validates request with `AnalyzeRequest`.
4. Backend preprocesses resume text conservatively.
5. Backend builds compact prompt and calls LLM.
6. Backend validates returned JSON with `AnalyzeResponse`.
7. Frontend renders score + tailored sections with copy actions.

---

## Setup and run

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Example `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=
MAX_RESUME_CHARS=12000
PREPROCESS_LOGGING_ENABLED=true
LOG_LEVEL=INFO
```

Use LM Studio local model (OpenAI-compatible server):

```env
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=google/gemma-4-e4b
OPENAI_BASE_URL=http://127.0.0.1:1234/v1
MAX_RESUME_CHARS=12000
PREPROCESS_LOGGING_ENABLED=true
LOG_LEVEL=INFO
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Optional `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Open: `http://localhost:3000`

---

## API contract

### `POST /analyze`

Request:

```json
{
  "resume_text": "string",
  "jd_text": "string"
}
```

Response:

```json
{
  "match_score": 78,
  "tailored_summary": "Backend engineer with strong API delivery experience...",
  "improved_bullets": [
    "Built and maintained FastAPI services supporting 99.9% uptime."
  ],
  "missing_keywords": ["Kubernetes", "Terraform"],
  "recruiter_feedback": [
    "Add one bullet quantifying scale and ownership in your latest role."
  ]
}
```

---

## How to extend this safely

This section explains how to evolve the MVP without breaking current behavior,
contracts, or evidence-safety guarantees.

### 1) Add PDF/DOCX upload

**What to add**
- Frontend file upload UI.
- Backend parsing module (for PDF/DOCX to plain text).
- Optional endpoint like `POST /extract-text` or multipart support in `/analyze`.

**Safety rules**
- Keep extracted raw text available for trace/debug.
- Run the same conservative preprocessing used for pasted text.
- Do not summarize away details before the main analyze step.

**Suggested structure**
- Add parser code under `backend/services/` (for example `document_parser.py`).
- Keep route handling in `main.py` and validation in `schemas.py`.

### 2) Add authentication

**What to add**
- API key or JWT-based auth middleware/dependency in FastAPI.
- Session/auth handling in frontend.

**Safety rules**
- Keep `/health` public, protect `/analyze`.
- Never log tokens or user secrets.
- Enforce per-user rate limits once auth is introduced.

**Suggested structure**
- Add auth logic in `backend/services/auth.py` or `backend/dependencies/auth.py`.
- Keep business logic (`llm.py`) independent of auth concerns.

### 3) Add caching to reduce cost

**What to add**
- Request fingerprinting (`resume_text + jd_text + model + prompt_version` hash).
- Cache store (Redis recommended for production).

**Safety rules**
- Use TTL (for example 24h) and explicit cache versioning.
- Invalidate cache when prompt/schema changes.
- Avoid caching any raw sensitive text in plain form.

**Suggested structure**
- Add `backend/services/cache.py` and call it from `llm.py`.
- Cache only validated response payloads.

### 4) Add async queue for heavy workloads

**What to add**
- Background jobs (Celery/RQ/Arq) for long-running analyses.
- Job status endpoints (`POST /analyze-async`, `GET /jobs/{id}`).

**Safety rules**
- Keep synchronous `/analyze` for fast path and fallback.
- Persist job metadata and failures for observability.
- Make retries idempotent using stable request keys.

**Suggested structure**
- Keep queue producer in API layer.
- Keep worker logic reusing `services/llm.py` so behavior remains consistent.

### 5) Add model routing/fallbacks

**What to add**
- Provider/model abstraction for primary + fallback models.
- Health-based or error-based fallback strategy.

**Safety rules**
- Same response schema regardless of model/provider.
- Keep strict output validation as a hard gate.
- Log which model served each request.

**Suggested structure**
- Add `backend/services/model_router.py`.
- Keep prompt contract centralized in `prompts.py`.

### 6) Add monitoring and quality controls

**What to add**
- Metrics: latency, error rate, token usage, cache hit rate.
- Quality checks on returned content shape and completeness.

**Safety rules**
- Log metadata only, never full resume/JD by default.
- Keep `request_id` end-to-end for traceability.

**Suggested structure**
- Add metrics wrappers in `main.py` and `llm.py`.
- Keep validation logic in `schemas.py` and add stricter validators over time.

### Extension checklist (before merging changes)

- API response schema remains backward compatible.
- Evidence-safety rules still enforced.
- Prompt changes are versioned and logged.
- Preprocessing remains deterministic and conservative.
- Sensitive data is not leaked in logs.
- Frontend handles new states (loading, errors, partial failures).
