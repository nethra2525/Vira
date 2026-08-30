interface ScoreBarProps {
  label: string;
  value: number; // 0-100
  tone?: "gold" | "sage";
}

export function ScoreBar({ label, value, tone = "gold" }: ScoreBarProps) {
  const barColor = tone === "gold" ? "bg-gold" : "bg-sage";
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-mist">{label}</span>
        <span className="font-mono text-paper">{Math.round(value)}%</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-pill bg-ink-raised">
        <div
          className={`h-full rounded-pill ${barColor} transition-all duration-500`}
          style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
        />
      </div>
    </div>
  );
}

export function OverallScoreRing({ score }: { score: number }) {
  const circumference = 2 * Math.PI * 42;
  const offset = circumference - (Math.max(0, Math.min(100, score)) / 100) * circumference;
  const tone = score >= 70 ? "#C9A227" : score >= 45 ? "#4F7A5A" : "#B5563A";

  return (
    <div className="relative flex h-28 w-28 items-center justify-center">
      <svg width="112" height="112" viewBox="0 0 96 96" className="-rotate-90">
        <circle cx="48" cy="48" r="42" fill="none" stroke="#2E3745" strokeWidth="7" />
        <circle
          cx="48"
          cy="48"
          r="42"
          fill="none"
          stroke={tone}
          strokeWidth="7"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-mono text-2xl font-medium text-paper">{Math.round(score)}%</span>
        <span className="text-[10px] uppercase tracking-wide text-mist-dim">match</span>
      </div>
    </div>
  );
}
