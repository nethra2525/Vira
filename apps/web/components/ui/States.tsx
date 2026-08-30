export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-ink-raised ${className}`} />;
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-card border border-dashed border-ink-border px-6 py-14 text-center">
      <h3 className="mb-1.5 font-display text-lg text-paper">{title}</h3>
      <p className="mb-5 max-w-sm text-sm text-mist">{description}</p>
      {action}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-card border border-rust/30 bg-rust/10 px-4 py-3 text-sm text-rust-bright">
      {message}
    </div>
  );
}
