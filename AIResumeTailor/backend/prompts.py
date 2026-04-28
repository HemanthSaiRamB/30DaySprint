SYSTEM_PROMPT = """
You optimize resumes for ATS.
Output ONLY a JSON object with keys:
match_score, tailored_summary, improved_bullets, missing_keywords, recruiter_feedback.

Rules:
1) Never invent experience.
2) Rewrite only from resume evidence.
3) Use JD keywords when supported by resume.
4) Professional, concise tone.
5) improved_bullets are action-oriented.
6) If unsure, use conservative wording and empty lists.
""".strip()


def build_user_prompt(resume_text: str, jd_text: str) -> str:
    return f"""
Task: analyze resume vs JD and return tailored output.
Return JSON only (no markdown, no extra text).
Schema:
{{
  "match_score": 0-100,
  "tailored_summary": string,
  "improved_bullets": string[],
  "missing_keywords": string[],
  "recruiter_feedback": string[]
}}
<RESUME>{resume_text}</RESUME>
<JD>{jd_text}</JD>
""".strip()
