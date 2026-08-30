"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch, ApiError, setStoredRole, setToken } from "@/lib/api";
import { UserOut } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Input, Label } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/States";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await apiFetch<{ access_token: string }>("/auth/login", {
        method: "POST",
        auth: false,
        body: { email, password },
      });
      setToken(tokens.access_token);

      const me = await apiFetch<UserOut>("/auth/me");
      setStoredRole(me.role);

      router.push(me.role === "recruiter" ? "/recruiter" : "/candidate");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function fillDemo(role: "candidate" | "recruiter") {
    if (role === "candidate") {
      setEmail("priya.candidate@viradmo.dev");
    } else {
      setEmail("arjun.recruiter@northwindanalytics.dev");
    }
    setPassword("DemoPass123!");
  }

  return (
    <div className="mx-auto flex max-w-sm flex-col px-6 py-20">
      <h1 className="font-display text-2xl font-semibold text-paper">Log in to VIRA</h1>
      <p className="mt-1.5 text-sm text-mist">Pick up where you left off.</p>

      <Card className="mt-8 p-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && <ErrorState message={error} />}

          <Button type="submit" disabled={loading} className="mt-1 w-full">
            {loading ? "Logging in..." : "Log in"}
          </Button>
        </form>

        <div className="mt-5 border-t border-ink-border pt-4 text-center text-xs text-mist-dim">
          Demo mode — try it instantly
          <div className="mt-2 flex justify-center gap-2">
            <button
              type="button"
              onClick={() => fillDemo("candidate")}
              className="rounded-pill border border-ink-border px-3 py-1 text-mist hover:border-gold/40 hover:text-paper"
            >
              Fill candidate demo
            </button>
            <button
              type="button"
              onClick={() => fillDemo("recruiter")}
              className="rounded-pill border border-ink-border px-3 py-1 text-mist hover:border-gold/40 hover:text-paper"
            >
              Fill recruiter demo
            </button>
          </div>
        </div>
      </Card>

      <p className="mt-6 text-center text-sm text-mist">
        New to VIRA?{" "}
        <Link href="/register" className="text-gold hover:text-gold-bright">
          Create an account
        </Link>
      </p>
    </div>
  );
}
