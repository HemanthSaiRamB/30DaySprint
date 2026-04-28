from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, description="Candidate resume content")
    jd_text: str = Field(..., min_length=50, description="Job description content")

    @field_validator("resume_text", "jd_text")
    @classmethod
    def strip_and_validate(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 50:
            raise ValueError("Input must contain at least 50 non-whitespace characters.")
        return cleaned


class AnalyzeResponse(BaseModel):
    match_score: int = Field(..., ge=0, le=100)
    tailored_summary: str = Field(..., min_length=20)
    improved_bullets: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    recruiter_feedback: list[str] = Field(default_factory=list)

    @field_validator("improved_bullets", "missing_keywords", "recruiter_feedback")
    @classmethod
    def validate_non_empty_items(cls, values: list[str]) -> list[str]:
        cleaned = [item.strip() for item in values if item.strip()]
        return cleaned
