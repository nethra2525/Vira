"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import { GrowthPathOut } from "@/lib/types";
import { Card, Badge } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { OverallScoreRing } from "@/components/ui/ScoreBar";
import { Skeleton, ErrorState } from "@/components/ui/States";
import RouteVisual from "@/components/vira/RouteVisual";

export default function GrowthPathPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const router = useRouter();

  const [growth, setGrowth] = useState<GrowthPathOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<GrowthPathOut>(`/matching/${jobId}/growth-path`)
      .then(setGrowth)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          router.push("/login");
          return;
        }
        setError(err instanceof ApiError ? err.message : "Couldn't load your growth path.");
      });
  }, [jobId, router]);

  if (!growth && !error) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="mt-6 h-56 w-full" />
      </div>
    );
  }

  if (error && !growth) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16">
        <ErrorState message={error} />
      </div>
    );
  }

  const improved = growth!.previous_match !== null && growth!.current_match > (growth!.previous_match ?? 0);

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <Link href="/candidate" className="text-xs text-mist hover:text-paper">
        ← Back to dashboard
      </Link>

      <h1 className="mt-3 font-display text-2xl font-semibold text-paper">Your VIRA Growth Path</h1>
      <p className="mt-1.5 text-sm text-mist">
        You're not being turned away — here's exactly what would move the needle.
      </p>

      <Card className="mt-8 overflow-hidden p-6">
        <RouteVisual compact />
      </Card>

      <div className="mt-6 grid gap-6 sm:grid-cols-[auto_1fr] sm:items-center">
        <div className="flex justify-center">
          <OverallScoreRing score={growth!.current_match} />
        </div>
        <div>
          <p className="font-display text-lg font-semibold text-paper">Current role match</p>
          {growth!.previous_match !== null && growth!.previous_match > 0 && (
            <p className={`mt-1 text-sm ${improved ? "text-sage-bright" : "text-mist"}`}>
              {improved
                ? `Up from ${growth!.previous_match}% since your last check — nice progress.`
                : `Previous match: ${growth!.previous_match}%`}
            </p>
          )}
        </div>
      </div>

      <div className="mt-8 grid gap-5 sm:grid-cols-2">
        <Card className="p-5">
          <h2 className="font-display text-sm font-semibold text-sage-bright">Your strengths</h2>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {growth!.strengths.length > 0 ? (
              growth!.strengths.map((s) => (
                <Badge key={s} tone="sage">
                  {s}
                </Badge>
              ))
            ) : (
              <p className="text-xs text-mist">Upload a resume to surface your demonstrated skills.</p>
            )}
          </div>
        </Card>

        <Card className="p-5">
          <h2 className="font-display text-sm font-semibold text-gold">Skills to improve</h2>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {growth!.skills_to_improve.length > 0 ? (
              growth!.skills_to_improve.map((s) => (
                <Badge key={s} tone="gold">
                  {s}
                </Badge>
              ))
            ) : (
              <p className="text-xs text-mist">You're matched on every listed skill for this role.</p>
            )}
          </div>
        </Card>
      </div>

      <div className="mt-8">
        <h2 className="font-display text-lg font-semibold text-paper">Recommended next steps</h2>
        <ol className="mt-4 flex flex-col gap-3">
          {growth!.steps.map((step) => (
            <li key={step.order} className="flex items-start gap-3 rounded-card border border-ink-border bg-ink-surface p-4">
              <span className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-pill bg-gold/15 font-mono text-xs text-gold">
                {step.order}
              </span>
              <p className="text-sm text-paper">{step.action}</p>
            </li>
          ))}
        </ol>
      </div>

      <p className="mt-8 text-xs leading-relaxed text-mist-dim">
        You may become eligible for reassessment after demonstrating improvement. This growth path
        reflects an AI-assisted comparison of your profile against this role's requirements — a human
        reviewer makes the final call on every hiring decision.
      </p>
    </div>
  );
}
