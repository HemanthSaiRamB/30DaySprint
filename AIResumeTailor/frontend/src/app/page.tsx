"use client";

import { FormEvent, useMemo, useState } from "react";

import { CopyButton } from "@/components/copy-button";
import { AnalyzeResponse, analyzeResume } from "@/lib/api";

export default function HomePage() {
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);

  const canAnalyze = useMemo(() => {
    return resumeText.trim().length >= 50 && jdText.trim().length >= 50;
  }, [resumeText, jdText]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);

    try {
      const data = await analyzeResume({
        resume_text: resumeText,
        jd_text: jdText,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto w-full max-w-6xl space-y-6">
        <header className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            AI Resume Tailor
          </h1>
          <p className="mt-2 text-sm text-slate-600 sm:text-base">
            Paste your resume and target job description to generate ATS-focused,
            evidence-based tailoring suggestions.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 gap-4 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 lg:grid-cols-2"
        >
          <div className="space-y-2">
            <label htmlFor="resume" className="text-sm font-semibold text-slate-700">
              Resume Text
            </label>
            <textarea
              id="resume"
              value={resumeText}
              onChange={(event) => setResumeText(event.target.value)}
              placeholder="Paste your current resume content..."
              className="h-72 w-full rounded-xl border border-slate-300 p-3 text-sm outline-none ring-brand-500 transition focus:ring-2"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="jd" className="text-sm font-semibold text-slate-700">
              Job Description
            </label>
            <textarea
              id="jd"
              value={jdText}
              onChange={(event) => setJdText(event.target.value)}
              placeholder="Paste the target job description..."
              className="h-72 w-full rounded-xl border border-slate-300 p-3 text-sm outline-none ring-brand-500 transition focus:ring-2"
            />
          </div>

          <div className="lg:col-span-2">
            <button
              type="submit"
              disabled={!canAnalyze || loading}
              className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-500 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading ? (
                <>
                  <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-r-transparent" />
                  Analyzing...
                </>
              ) : (
                "Analyze"
              )}
            </button>
          </div>
        </form>

        {error ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        {result ? (
          <section className="space-y-4">
            <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-900">Match Score</h2>
              </div>
              <p className="mt-3 text-4xl font-bold text-brand-600">
                {result.match_score}%
              </p>
            </article>

            <ResultCard title="Tailored Summary" content={result.tailored_summary} />
            <ResultListCard
              title="Improved Bullets"
              items={result.improved_bullets}
              emptyLabel="No improved bullets returned."
            />
            <ResultListCard
              title="Missing Keywords"
              items={result.missing_keywords}
              emptyLabel="No missing keywords returned."
            />
            <ResultListCard
              title="Recruiter Feedback"
              items={result.recruiter_feedback}
              emptyLabel="No recruiter feedback returned."
            />
          </section>
        ) : null}
      </div>
    </main>
  );
}

function ResultCard({ title, content }: { title: string; content: string }) {
  return (
    <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
        <CopyButton value={content} />
      </div>
      <p className="mt-3 whitespace-pre-wrap text-sm text-slate-700">{content}</p>
    </article>
  );
}

function ResultListCard({
  title,
  items,
  emptyLabel,
}: {
  title: string;
  items: string[];
  emptyLabel: string;
}) {
  return (
    <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
        <CopyButton value={items.join("\n")} />
      </div>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">{emptyLabel}</p>
      ) : (
        <ul className="mt-3 list-disc space-y-2 pl-6 text-sm text-slate-700">
          {items.map((item) => (
            <li key={`${title}-${item}`}>{item}</li>
          ))}
        </ul>
      )}
    </article>
  );
}
