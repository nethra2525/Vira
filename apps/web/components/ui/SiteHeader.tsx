"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearToken, getStoredRole } from "@/lib/api";
import Button from "./Button";

export default function SiteHeader() {
  const [role, setRole] = useState<string | null>(null);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    setRole(getStoredRole());
  }, [pathname]);

  const dashboardHref = role === "recruiter" ? "/recruiter" : "/candidate";

  function handleLogout() {
    clearToken();
    window.localStorage.removeItem("vira_role");
    setRole(null);
    router.push("/");
  }

  return (
    <header className="sticky top-0 z-40 border-b border-ink-border/60 bg-ink/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="font-display text-lg font-semibold tracking-tight text-paper">VIRA</span>
          <span className="hidden text-xs text-mist-dim sm:inline">Skills over background</span>
        </Link>

        <nav className="flex items-center gap-1.5">
          <Link
            href="/jobs"
            className="rounded-pill px-3.5 py-2 text-sm text-mist transition-colors hover:text-paper"
          >
            Explore Opportunities
          </Link>

          {role ? (
            <>
              <Link
                href={dashboardHref}
                className="rounded-pill px-3.5 py-2 text-sm text-mist transition-colors hover:text-paper"
              >
                Dashboard
              </Link>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                Log out
              </Button>
            </>
          ) : (
            <>
              <Link href="/login" className="rounded-pill px-3.5 py-2 text-sm text-mist hover:text-paper">
                Log in
              </Link>
              <Link href="/register">
                <Button size="sm">Get started</Button>
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
