"use client";

import { FormEvent, Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { apiFetch, ApiError, setStoredRole, setToken } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Input, Label } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/States";

function RegisterForm() {
  const router = useRouter();
  const params = useSearchParams();
  const initialRole = params.get("role") === "recruiter" ? "recruiter" : "candidate";

  const [role, setRole] = useState<"candidate" | "recruiter">(initialRole);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await apiFetch<{ access_token: string }>("/auth/register", {
        method: "POST",
        auth: false,
        body: {
          email,
          password,
          full_name: fullName,
          role,
          company_name: role === "recruiter" ? companyName : undefined,
        },
      });
      setToken(tokens.access_token);
      setStoredRole(role);
      router.push(role === "recruiter" ? "/recruiter" : "/candidate");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex max-w-sm flex-col px-6 py-20">
      <h1 className="font-display text-2xl font-semibold text-paper">Create your account</h1>
      <p className="mt-1.5 text-sm text-mist">Skills over background — for candidates and employers alike.</p>

      <div className="mt-6 flex gap-2 rounded-pill border border-ink-border bg-ink-raised p-1">
        {(["candidate", "recruiter"] as const).map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => setRole(r)}
            className={`flex-1 rounded-pill py-2 text-sm font-medium capitalize transition-colors ${
              role === r ? "bg-gold text-ink" : "text-mist hover:text-paper"
            }`}
          >
            {r === "candidate" ? "I'm a candidate" : "I'm hiring"}
          </button>
        ))}
      </div>

      <Card className="mt-6 p-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <Label htmlFor="fullName">Full name</Label>
            <Input id="fullName" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {role === "recruiter" && (
            <div>
              <Label htmlFor="companyName">Company name</Label>
              <Input
                id="companyName"
                required
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
              />
            </div>
          )}

          {error && <ErrorState message={error} />}

          <Button type="submit" disabled={loading} className="mt-1 w-full">
            {loading ? "Creating account..." : "Create account"}
          </Button>
        </form>
      </Card>

      <p className="mt-6 text-center text-sm text-mist">
        Already have an account?{" "}
        <Link href="/login" className="text-gold hover:text-gold-bright">
          Log in
        </Link>
      </p>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense>
      <RegisterForm />
    </Suspense>
  );
}
