"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import { JobOut } from "@/lib/types";
import { Card, Badge } from "@/components/ui/Card";
import { Input, Label, Textarea } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/States";

export default function NewJobPage() {
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [responsibilities, setResponsibilities] = useState("");
  const [location, setLocation] = useState("Remote");
  const [employmentType, setEmploymentType] = useState("Full-time");
  const [mustHaveInput, setMustHaveInput] = useState("");
  const [preferredInput, setPreferredInput] = useState("");
  const [mustHave, setMustHave] = useState<string[]>([]);
  const [preferred, setPreferred] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function addSkill(list: "must" | "preferred") {
    if (list === "must") {
      const value = mustHaveInput.trim();
      if (value && !mustHave.includes(value)) setMustHave([...mustHave, value]);
      setMustHaveInput("");
    } else {
      const value = preferredInput.trim();
      if (value && !preferred.includes(value)) setPreferred([...preferred, value]);
      setPreferredInput("");
    }
  }

  async function handleSubmit(e: FormEvent, publish: boolean) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const skills = [
        ...mustHave.map((name) => ({ name, requirement_type: "must_have" })),
        ...preferred.map((name) => ({ name, requirement_type: "preferred" })),
      ];
      const job = await apiFetch<JobOut>("/jobs", {
        method: "POST",
        body: {
          title,
          description,
          responsibilities,
          location,
          employment_type: employmentType,
          skills,
          status: publish ? "published" : "draft",
        },
      });
      router.push("/recruiter");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
        return;
      }
      setError(err instanceof ApiError ? err.message : "Couldn't create this job.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <Link href="/recruiter" className="text-xs text-mist hover:text-paper">
        ← Back to dashboard
      </Link>
      <h1 className="mt-3 font-display text-2xl font-semibold text-paper">Create a new role</h1>
      <p className="mt-1.5 text-sm text-mist">
        Separate must-have and preferred skills — this distinction directly shapes how VIRA scores candidates.
      </p>

      <Card className="mt-8 p-6">
        <form className="flex flex-col gap-5">
          <div>
            <Label htmlFor="title">Job title</Label>
            <Input id="title" required value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="location">Location</Label>
              <Input id="location" value={location} onChange={(e) => setLocation(e.target.value)} />
            </div>
            <div>
              <Label htmlFor="employmentType">Employment type</Label>
              <Input id="employmentType" value={employmentType} onChange={(e) => setEmploymentType(e.target.value)} />
            </div>
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              rows={4}
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div>
            <Label htmlFor="responsibilities">Responsibilities</Label>
            <Textarea
              id="responsibilities"
              rows={3}
              value={responsibilities}
              onChange={(e) => setResponsibilities(e.target.value)}
            />
          </div>

          <div>
            <Label htmlFor="mustHave">Must-have skills</Label>
            <div className="flex gap-2">
              <Input
                id="mustHave"
                value={mustHaveInput}
                onChange={(e) => setMustHaveInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addSkill("must");
                  }
                }}
                placeholder="e.g. SQL — press Enter to add"
              />
              <Button type="button" variant="secondary" size="sm" onClick={() => addSkill("must")}>
                Add
              </Button>
            </div>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {mustHave.map((s) => (
                <Badge key={s} tone="gold" className="cursor-pointer" onClick={() => setMustHave(mustHave.filter((x) => x !== s))}>
                  {s} ×
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <Label htmlFor="preferred">Preferred skills</Label>
            <div className="flex gap-2">
              <Input
                id="preferred"
                value={preferredInput}
                onChange={(e) => setPreferredInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addSkill("preferred");
                  }
                }}
                placeholder="e.g. Power BI — press Enter to add"
              />
              <Button type="button" variant="secondary" size="sm" onClick={() => addSkill("preferred")}>
                Add
              </Button>
            </div>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {preferred.map((s) => (
                <Badge key={s} tone="mist" className="cursor-pointer" onClick={() => setPreferred(preferred.filter((x) => x !== s))}>
                  {s} ×
                </Badge>
              ))}
            </div>
          </div>

          {error && <ErrorState message={error} />}

          <div className="flex gap-3">
            <Button type="button" variant="secondary" disabled={loading} onClick={(e) => handleSubmit(e, false)}>
              Save as draft
            </Button>
            <Button type="button" disabled={loading} onClick={(e) => handleSubmit(e, true)}>
              {loading ? "Publishing..." : "Publish role"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
