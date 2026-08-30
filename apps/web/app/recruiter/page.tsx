"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";
import { JobOut } from "@/lib/types";
import { Card, Badge } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Skeleton, EmptyState, ErrorState } from "@/components/ui/States";

export default function RecruiterDashboardPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<JobOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<JobOut[]>("/jobs/company/mine")
      .then(setJobs)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          router.push("/login");
          return;
        }
        setError(err instanceof ApiError ? err.message : "Couldn't load your jobs.");
      });
  }, [router]);

  const publishedCount = jobs?.filter((j) => j.status === "published").length ?? 0;
  const draftCount = jobs?.filter((j) => j.status === "draft").length ?? 0;

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-semibold text-paper">Recruiter dashboard</h1>
          <p className="mt-1.5 text-sm text-mist">Manage your open roles and review candidate matches.</p>
        </div>
        <Link href="/recruiter/jobs/new">
          <Button>+ New job</Button>
        </Link>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <Card className="p-5">
          <p className="text-xs uppercase tracking-wide text-mist-dim">Active jobs</p>
          <p className="mt-1.5 font-display text-2xl font-semibold text-paper">{publishedCount}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-wide text-mist-dim">Drafts</p>
          <p className="mt-1.5 font-display text-2xl font-semibold text-paper">{draftCount}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs uppercase tracking-wide text-mist-dim">Total roles</p>
          <p className="mt-1.5 font-display text-2xl font-semibold text-paper">{jobs?.length ?? 0}</p>
        </Card>
      </div>

      <div className="mt-10">
        <h2 className="font-display text-lg font-semibold text-paper">Your jobs</h2>

        <div className="mt-4 flex flex-col gap-3">
          {error && <ErrorState message={error} />}
          {!jobs && !error && (
            <>
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
            </>
          )}
          {jobs && jobs.length === 0 && (
            <EmptyState
              title="No jobs yet"
              description="Create your first role to start matching candidates by demonstrated skill."
              action={
                <Link href="/recruiter/jobs/new">
                  <Button size="sm">+ New job</Button>
                </Link>
              }
            />
          )}
          {jobs?.map((job) => (
            <Card key={job.id} className="flex flex-wrap items-center justify-between gap-3 p-4">
              <div>
                <p className="font-display text-sm font-semibold text-paper">{job.title}</p>
                <p className="mt-1 text-xs text-mist">
                  {job.location} · {job.employment_type}
                </p>
              </div>
              <Badge tone={job.status === "published" ? "sage" : "mist"}>{job.status}</Badge>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
