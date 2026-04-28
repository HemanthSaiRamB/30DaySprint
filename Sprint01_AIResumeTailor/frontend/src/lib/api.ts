export interface AnalyzeRequest {
  resume_text: string;
  jd_text: string;
}

export interface AnalyzeResponse {
  match_score: number;
  tailored_summary: string;
  improved_bullets: string[];
  missing_keywords: string[];
  recruiter_feedback: string[];
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function analyzeResume(
  payload: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail = "Something went wrong while analyzing.";
    try {
      const data = await response.json();
      detail = data?.detail ?? detail;
    } catch {
      // No-op fallback to default message.
    }
    throw new Error(detail);
  }

  return response.json();
}
