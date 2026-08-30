import Link from "next/link";
import Button from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import RouteVisual from "@/components/vira/RouteVisual";

const HOW_IT_WORKS = [
  {
    title: "Build your profile",
    body: "Upload a resume or fill in your skills directly. VIRA extracts and normalizes what you can already do.",
  },
  {
    title: "Discover your match",
    body: "See a transparent score against real roles — never a black box, always a breakdown you can inspect.",
  },
  {
    title: "Demonstrate your skills",
    body: "Prove readiness through role-specific assessments and scenario rounds, scored against clear rubrics.",
  },
  {
    title: "Grow and improve",
    body: "Not a match yet? Get a specific route: the skills to learn and the steps to close the gap.",
  },
  {
    title: "Connect with opportunities",
    body: "Apply with evidence behind you, and request reassessment once you've closed the gap.",
  },
];

const WHY_VIRA = [
  {
    title: "Skills over background",
    body: "Degrees and pedigree don't disappear, but they don't gate you either. Demonstrated ability leads.",
  },
  {
    title: "Explainable by default",
    body: "Every score ships with its breakdown and a plain-language reason. Ask \u201cwhy\u201d and get a real answer.",
  },
  {
    title: "Second chances, built in",
    body: "A low match isn't a door closing — it's a route VIRA lays out, with a path back to reassessment.",
  },
  {
    title: "Human review, always",
    body: "VIRA recommends. People decide. Every AI output is a starting point for a human reviewer, not a verdict.",
  },
];

export default function LandingPage() {
  return (
    <div>
      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 pb-20 pt-16 sm:pt-24">
        <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_1fr]">
          <div>
            <span className="mb-5 inline-flex items-center gap-2 rounded-pill border border-gold/25 bg-gold/10 px-3 py-1 text-xs font-medium text-gold-bright">
              Skills Over Background. Opportunities for Everyone.
            </span>
            <h1 className="text-balance font-display text-4xl font-semibold leading-[1.08] text-paper sm:text-5xl">
              Your skills deserve to be seen.
            </h1>
            <p className="mt-5 max-w-lg text-balance text-base leading-relaxed text-mist sm:text-lg">
              VIRA uses AI-assisted matching and skill-based assessments to connect people with
              relevant opportunities — and lays out a clear route forward when you're not quite
              there yet.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/jobs">
                <Button size="lg">Explore Opportunities</Button>
              </Link>
              <Link href="/register?role=recruiter">
                <Button size="lg" variant="secondary">
                  For Employers
                </Button>
              </Link>
            </div>
          </div>

          <Card className="p-6">
            <p className="mb-1 text-xs uppercase tracking-wide text-mist-dim">Your growth path, visualized</p>
            <RouteVisual />
          </Card>
        </div>
      </section>

      {/* How VIRA works */}
      <section className="border-t border-ink-border/60 bg-ink-surface/40 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-10 font-display text-2xl font-semibold text-paper">How VIRA works</h2>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-5">
            {HOW_IT_WORKS.map((step, i) => (
              <div key={step.title}>
                <span className="font-mono text-xs text-gold">{String(i + 1).padStart(2, "0")}</span>
                <h3 className="mt-2 font-display text-base font-semibold text-paper">{step.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-mist">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why VIRA */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-10 font-display text-2xl font-semibold text-paper">Why VIRA</h2>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {WHY_VIRA.map((item) => (
              <Card key={item.title} className="p-5">
                <h3 className="font-display text-base font-semibold text-paper">{item.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-mist">{item.body}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-ink-border/60 py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-6 text-xs text-mist-dim sm:flex-row">
          <span>VIRA — Virtual Intelligent Recruitment Assistant</span>
          <span>AI-assisted recommendations, human-made decisions.</span>
        </div>
      </footer>
    </div>
  );
}
