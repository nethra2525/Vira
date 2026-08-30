"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";
import { CandidateDashboard, ParsedResumeOut } from "@/lib/types";
import { Card, Badge } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Skeleton, EmptyState, ErrorState } from "@/components/ui/States";

const STATUS_TONE: Record<string, "gold" | "sage" | "rust" | "mist"> = {
  applied: "mist",
  under_review: "gold",
  assessment: "gold",
  interview: "sage",
  growth_path: "rust",
  shortlisted: "sage",
  rejected: "rust",
  hired: "sage",
};

export default function CandidateDashboardPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [dashboard, setDashboard] = useState<CandidateDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<ParsedResumeOut | null>(null);

  function loadDashboard() {
    apiFetch<CandidateDashboard>("/candidates/me/dashboard")
      .then(setDashboard)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          router.push("/login");
          return;
        }
        setError(err instanceof ApiError ? err.message : "Couldn't load your dashboard.");
      });
  }

  useEffect(loadDashboard, [router]);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const result = await apiFetch<ParsedResumeOut>("/resumes/upload", { method: "POST", formData });
      setUploadResult(result);
      loadDashboard();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't process that resume.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  if (!dashboard && !error) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-16">
        <Skeleton className="h-8 w-1/3" />
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
      </div>
    );
  }

  if (error && !dashboard) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-16">
        <ErrorState message={error} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="font-display text-2xl font-semibold text-paper">
        Good to see you, {dashboard!.welcome_name}.
      </h1>
      <p className="mt-1.5 text-sm text-mist">Here's where things stand.</p>

      {/* Career overview */}
      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <Card className="p-5">
          <p className="text-xs uppercase tracking-wide text-mist-dim">Applications</p>
          <p className="mt-1.5 font-display text-2xl font-semibold text-paper">
            {dashboard!.career_overview.applications}
          </p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-wide text-mist-dim">Interviews scheduled</p>
          <p className="mt-1.5 font-display text-2xl font-semibold text-paper">
            {dashboard!.career_overview.interviews_scheduled}
          </p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-wide text-mist-dim">Average match score</p>
          <p className="mt-1.5 font-display text-2xl font-semibold text-paper">
            {dashboard!.career_overview.average_match_score}%
          </p>
        </Card>
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-[1fr_320px]">
        {/* Applications list */}
        <section>
          <h2 className="font-display text-lg font-semibold text-paper">Your applications</h2>
          <div className="mt-4 flex flex-col gap-3">
            {dashboard!.applications.length === 0 && (
              <EmptyState
                title="No applications yet"
                description="Explore open roles and apply once you've checked your match score."
                action={
                  <Link href="/jobs">
                    <Button size="sm">Explore Opportunities</Button>
                  </Link>
                }
              />
            )}
            {dashboard!.applications.map((app) => (
              <Card key={app.id} className="flex items-center justify-between p-4">
                <div>
                  <Link href={`/jobs/${app.job_id}`} className="font-display text-sm font-semibold text-paper hover:text-gold">
                    {app.job_title}
                  </Link>
                  <p className="mt-1 font-mono text-xs text-mist">{app.match_score}% match</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge tone={STATUS_TONE[app.status] || "mist"}>{app.status.replace("_", " ")}</Badge>
                  <Link href={`/candidate/growth-path/${app.job_id}`}>
                    <Button size="sm" variant="ghost">
                      Growth path
                    </Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        </section>

        {/* Resume upload */}
        <aside>
          <Card className="p-5">
            <h2 className="font-display text-base font-semibold text-paper">Resume</h2>
            <p className="mt-1.5 text-xs text-mist">
              Upload to update your detected skills. Profile completion: {dashboard!.profile_completion}%
            </p>

            <div className="mt-3 h-1.5 w-full overflow-hidden rounded-pill bg-ink-raised">
              <div
                className="h-full rounded-pill bg-gold transition-all"
                style={{ width: `${dashboard!.profile_completion}%` }}
              />
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              className="hidden"
              onChange={handleFileChange}
            />
            <Button
              variant="secondary"
              size="sm"
              className="mt-4 w-full"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? "Analyzing resume..." : "Upload resume"}
            </Button>

            {uploadResult && (
              <div className="mt-4 rounded-lg border border-sage/25 bg-sage/10 p-3">
                <p className="text-xs font-medium text-sage-bright">Detected skills</p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {uploadResult.detected_skills.map((s) => (
                    <Badge key={s} tone="sage">
                      {s}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {error && <div className="mt-3"><ErrorState message={error} /></div>}
          </Card>
        </aside>
      </div>
    </div>
  );
}
