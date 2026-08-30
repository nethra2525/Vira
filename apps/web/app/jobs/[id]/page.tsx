"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError, getStoredRole } from "@/lib/api";
import { JobOut, MatchResult } from "@/lib/types";
import { Card, Badge } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { OverallScoreRing, ScoreBar } from "@/components/ui/ScoreBar";
import { Skeleton, ErrorState } from "@/components/ui/States";

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [job, setJob] = useState<JobOut | null>(null);
  const [match, setMatch] = useState<MatchResult | null>(null);
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [loadingMatch, setLoadingMatch] = useState(false);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    setRole(getStoredRole());
    apiFetch<JobOut>(`/jobs/${id}`, { auth: false })
      .then(setJob)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load this job."));
  }, [id]);

  async function analyzeMatch() {
    setLoadingMatch(true);
    setError(null);
    try {
      const result = await apiFetch<MatchResult>(`/matching/analyze?job_id=${id}`, { method: "POST" });
      setMatch(result);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
        return;
      }
      setError(err instanceof ApiError ? err.message : "Couldn't analyze your match right now.");
    } finally {
      setLoadingMatch(false);
    }
  }

  async function apply() {
    setApplying(true);
    setError(null);
    try {
      await apiFetch(`/matching/${id}/apply`, { method: "POST" });
      setApplied(true);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
        return;
      }
      setError(err instanceof ApiError ? err.message : "Couldn't submit your application.");
    } finally {
      setApplying(false);
    }
  }

  if (!job && !error) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="mt-4 h-40 w-full" />
      </div>
    );
  }

  if (error && !job) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16">
        <ErrorState message={error} />
      </div>
    );
  }

  return (
    <div className="mx-auto grid max-w-4xl gap-8 px-6 py-16 lg:grid-cols-[1fr_320px]">
      <div>
        <Link href="/jobs" className="text-xs text-mist hover:text-paper">
          ← All opportunities
        </Link>
        <h1 className="mt-3 font-display text-2xl font-semibold text-paper">{job!.title}</h1>
        <p className="mt-1 text-sm text-mist">
          {job!.company_name} · {job!.location} · {job!.employment_type}
        </p>

        <div className="mt-5 flex flex-wrap gap-1.5">
          {job!.must_have_skills.map((s) => (
            <Badge key={s} tone="gold">
              {s} · required
            </Badge>
          ))}
          {job!.preferred_skills.map((s) => (
            <Badge key={s} tone="mist">
              {s} · preferred
            </Badge>
          ))}
        </div>

        <div className="mt-8 space-y-5">
          <section>
            <h2 className="font-display text-base font-semibold text-paper">About this role</h2>
            <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-mist">{job!.description}</p>
          </section>
          {job!.responsibilities && (
            <section>
              <h2 className="font-display text-base font-semibold text-paper">Responsibilities</h2>
              <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-mist">{job!.responsibilities}</p>
            </section>
          )}
        </div>

        {error && job && <div className="mt-5"><ErrorState message={error} /></div>}
      </div>

      {/* Match sidebar */}
      <aside className="lg:sticky lg:top-24 lg:self-start">
        <Card className="p-5">
          {!match && (
            <>
              <p className="text-sm text-mist">
                {role === "recruiter"
                  ? "Match scoring is available for candidate accounts."
                  : "See exactly how your profile lines up with this role."}
              </p>
              {role !== "recruiter" && (
                <Button className="mt-4 w-full" onClick={analyzeMatch} disabled={loadingMatch}>
                  {loadingMatch ? "Analyzing..." : "Check my match score"}
                </Button>
              )}
            </>
          )}

          {match && (
            <>
              <div className="flex justify-center">
                <OverallScoreRing score={match.overall_score} />
              </div>

              <button
                onClick={() => setShowBreakdown((v) => !v)}
                className="mt-4 w-full text-center text-xs font-medium text-gold hover:text-gold-bright"
              >
                {showBreakdown ? "Hide" : "Why this match score?"}
              </button>

              {showBreakdown && (
                <div className="mt-4 space-y-3">
                  <ScoreBar label="Skills match" value={match.breakdown.skills_match} />
                  <ScoreBar label="Experience relevance" value={match.breakdown.experience_relevance} tone="sage" />
                  <ScoreBar label="Project relevance" value={match.breakdown.project_relevance} />
                  <ScoreBar label="Assessment readiness" value={match.breakdown.assessment_readiness} tone="sage" />

                  <p className="mt-3 text-xs leading-relaxed text-mist">{match.explanation}</p>

                  {match.missing_must_have.length > 0 && (
                    <div className="rounded-lg border border-rust/25 bg-rust/10 p-3">
                      <p className="text-xs font-medium text-rust-bright">Missing requirements</p>
                      <p className="mt-1 text-xs text-mist">{match.missing_must_have.join(", ")}</p>
                    </div>
                  )}

                  <Link href={`/candidate/growth-path/${id}`}>
                    <Button variant="secondary" size="sm" className="mt-2 w-full">
                      View my Growth Path
                    </Button>
                  </Link>
                </div>
              )}

              <p className="mt-4 text-[11px] leading-relaxed text-mist-dim">{match.disclaimer}</p>
            </>
          )}

          {role === "candidate" && (
            <Button
              className="mt-4 w-full"
              variant={applied ? "secondary" : "primary"}
              onClick={apply}
              disabled={applying || applied}
            >
              {applied ? "Applied ✓" : applying ? "Submitting..." : "Apply to this role"}
            </Button>
          )}
        </Card>
      </aside>
    </div>
  );
}
