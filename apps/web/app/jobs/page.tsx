"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import { JobOut } from "@/lib/types";
import { Card, Badge } from "@/components/ui/Card";
import { Skeleton, EmptyState, ErrorState } from "@/components/ui/States";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<JobOut[]>("/jobs", { auth: false })
      .then(setJobs)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load jobs."));
  }, []);

  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="font-display text-2xl font-semibold text-paper">Explore opportunities</h1>
      <p className="mt-1.5 text-sm text-mist">
        Roles listed here weigh demonstrated skill first. Log in as a candidate to see your match score.
      </p>

      <div className="mt-8 flex flex-col gap-4">
        {error && <ErrorState message={error} />}

        {!jobs && !error && (
          <>
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
          </>
        )}

        {jobs && jobs.length === 0 && (
          <EmptyState
            title="No open roles right now"
            description="Check back soon — new opportunities are added regularly."
          />
        )}

        {jobs?.map((job) => (
          <Link key={job.id} href={`/jobs/${job.id}`}>
            <Card className="p-5 transition-colors hover:border-gold/40">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <h2 className="font-display text-lg font-semibold text-paper">{job.title}</h2>
                  <p className="mt-0.5 text-sm text-mist">
                    {job.company_name} · {job.location} · {job.employment_type}
                  </p>
                </div>
              </div>
              <p className="mt-3 line-clamp-2 text-sm text-mist">{job.description}</p>
              <div className="mt-4 flex flex-wrap gap-1.5">
                {job.must_have_skills.map((s) => (
                  <Badge key={s} tone="gold">
                    {s}
                  </Badge>
                ))}
                {job.preferred_skills.map((s) => (
                  <Badge key={s} tone="mist">
                    {s}
                  </Badge>
                ))}
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
