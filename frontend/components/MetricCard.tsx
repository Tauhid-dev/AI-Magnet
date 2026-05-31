type MetricCardProps = {
  label: string;
  value: string | number;
  detail?: string;
};

export function MetricCard({ label, value, detail }: MetricCardProps) {
  return (
    <div className="rounded-lg border border-line bg-panel px-4 py-4 shadow-[0_10px_26px_rgba(16,24,40,0.05)]">
      <div className="text-xs font-semibold uppercase text-muted">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-ink">{value}</div>
      {detail ? (
        <div className="mt-3 inline-flex rounded-md bg-accent/10 px-2 py-1 text-xs font-semibold text-accent">
          {detail}
        </div>
      ) : null}
    </div>
  );
}
