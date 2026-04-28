import logging
import os
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import AnalyzeRequest, AnalyzeResponse
from services.llm import LLMServiceError, analyze_resume_with_llm

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Resume Tailor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    request_id = str(uuid.uuid4())
    logger.info(
        "analyze_request_started request_id=%s resume_chars=%s jd_chars=%s",
        request_id,
        len(payload.resume_text),
        len(payload.jd_text),
    )
    try:
        result = analyze_resume_with_llm(
            resume_text=payload.resume_text,
            jd_text=payload.jd_text,
        )
        logger.info(
            "analyze_request_succeeded request_id=%s match_score=%s",
            request_id,
            result.match_score,
        )
        return result
    except LLMServiceError as exc:
        logger.exception("analyze_request_failed request_id=%s", request_id)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
