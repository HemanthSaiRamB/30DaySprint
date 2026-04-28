import json
import logging
import os
import re

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from prompts import SYSTEM_PROMPT, build_user_prompt
from schemas import AnalyzeResponse

load_dotenv()

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None
MAX_RESUME_CHARS = int(os.getenv("MAX_RESUME_CHARS", "12000"))
PREPROCESS_LOGGING_ENABLED = os.getenv("PREPROCESS_LOGGING_ENABLED", "true").lower() == "true"
logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    pass


def build_request_args(user_content: str) -> dict:
    request_args = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
    }
    # Some local OpenAI-compatible servers (e.g. LM Studio) do not support json_object.
    if not OPENAI_BASE_URL:
        request_args["response_format"] = {"type": "json_object"}
    return request_args


def repair_json_with_model(client: OpenAI, raw_content: str) -> dict:
    repair_prompt = f"""
Fix the JSON below and return ONLY valid JSON.
Do not add new facts. Keep the same meaning and schema keys:
match_score, tailored_summary, improved_bullets, missing_keywords, recruiter_feedback.

JSON to fix:
{raw_content}
""".strip()

    repair_args = build_request_args(repair_prompt)
    repair_args["temperature"] = 0
    completion = client.chat.completions.create(**repair_args)
    repaired_content = completion.choices[0].message.content or "{}"
    return extract_json_object(repaired_content)


def extract_json_object(raw_content: str) -> dict:
    candidate = raw_content.strip()
    if not candidate:
        raise json.JSONDecodeError("Empty content", candidate, 0)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(candidate[start : end + 1])


def preprocess_resume_text(raw_text: str) -> tuple[str, dict[str, int | bool]]:
    """
    Conservative cleanup:
    - normalize whitespace
    - drop obvious non-evidence noise lines
    - deduplicate exact repeated lines
    - cap very long resumes while preserving front-loaded evidence
    """
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.split("\n")]

    noise_patterns = [
        re.compile(r"^page\s+\d+(\s+of\s+\d+)?$", re.IGNORECASE),
        re.compile(r"^resume\s+generated\s+by\b", re.IGNORECASE),
        re.compile(r"^curriculum\s+vitae$", re.IGNORECASE),
        re.compile(r"^[-_=]{3,}$"),
    ]

    cleaned_lines: list[str] = []
    seen: set[str] = set()
    removed_noise_count = 0
    removed_duplicate_count = 0

    for line in lines:
        if not line:
            cleaned_lines.append("")
            continue
        if any(pattern.match(line) for pattern in noise_patterns):
            removed_noise_count += 1
            continue
        if line in seen:
            removed_duplicate_count += 1
            continue
        seen.add(line)
        cleaned_lines.append(line)

    # Collapse consecutive blank lines.
    compact_lines: list[str] = []
    prev_blank = False
    for line in cleaned_lines:
        is_blank = line == ""
        if is_blank and prev_blank:
            continue
        compact_lines.append(line)
        prev_blank = is_blank

    cleaned = "\n".join(compact_lines).strip()

    # Evidence safety guard: if cleanup is too aggressive, fall back to normalized text.
    used_fallback = False
    if len(cleaned) < int(len(normalized.strip()) * 0.7):
        cleaned = normalized.strip()
        used_fallback = True

    truncated = False
    if len(cleaned) > MAX_RESUME_CHARS:
        cleaned = cleaned[:MAX_RESUME_CHARS].rsplit("\n", 1)[0].strip()
        truncated = True

    stats: dict[str, int | bool] = {
        "original_chars": len(raw_text),
        "normalized_chars": len(normalized.strip()),
        "cleaned_chars": len(cleaned),
        "removed_noise_lines": removed_noise_count,
        "removed_duplicate_lines": removed_duplicate_count,
        "used_fallback": used_fallback,
        "truncated": truncated,
    }
    return cleaned, stats


def analyze_resume_with_llm(resume_text: str, jd_text: str) -> AnalyzeResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and not OPENAI_BASE_URL:
        raise LLMServiceError("OPENAI_API_KEY is missing in environment.")
    if not api_key and OPENAI_BASE_URL:
        # LM Studio/OpenAI-compatible local servers typically accept any non-empty key.
        api_key = "lm-studio"

    client = OpenAI(api_key=api_key, base_url=OPENAI_BASE_URL)
    processed_resume_text, preprocess_stats = preprocess_resume_text(resume_text)
    if PREPROCESS_LOGGING_ENABLED:
        logger.info("resume_preprocess_stats=%s", preprocess_stats)

    user_prompt = build_user_prompt(
        resume_text=processed_resume_text,
        jd_text=jd_text,
    )

    try:
        logger.info(
            "llm_request_started model=%s base_url=%s resume_chars=%s jd_chars=%s",
            DEFAULT_MODEL,
            OPENAI_BASE_URL or "https://api.openai.com/v1",
            preprocess_stats["cleaned_chars"],
            len(jd_text),
        )
        completion = client.chat.completions.create(**build_request_args(user_prompt))
        raw_content = completion.choices[0].message.content or "{}"
        try:
            payload = extract_json_object(raw_content)
        except json.JSONDecodeError:
            logger.warning("llm_response_invalid_json_attempting_repair")
            payload = repair_json_with_model(client, raw_content)
        logger.info("llm_request_succeeded response_chars=%s", len(raw_content))
        return AnalyzeResponse.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.exception("llm_response_validation_failed")
        raise LLMServiceError(f"Invalid LLM response format: {exc}") from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("llm_request_failed")
        raise LLMServiceError(f"LLM request failed: {exc}") from exc
