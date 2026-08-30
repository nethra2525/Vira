import { HTMLAttributes } from "react";

export function Card({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-card border border-ink-border bg-ink-surface shadow-soft ${className}`}
      {...props}
    />
  );
}

type BadgeTone = "gold" | "sage" | "rust" | "mist";

const toneClasses: Record<BadgeTone, string> = {
  gold: "bg-gold/15 text-gold-bright border-gold/30",
  sage: "bg-sage/15 text-sage-bright border-sage/30",
  rust: "bg-rust/15 text-rust-bright border-rust/30",
  mist: "bg-mist/10 text-mist border-mist/25",
};

export function Badge({
  tone = "mist",
  className = "",
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: BadgeTone }) {
  return (
    <span
      className={`inline-flex items-center rounded-pill border px-2.5 py-1 text-xs font-medium ${toneClasses[tone]} ${className}`}
      {...props}
    />
  );
}
