type MetricCardProps = {
  label: string;
  value: string | number;
  detail?: string;
};

export function MetricCard({ label, value, detail }: MetricCardProps) {
  return (
    <div className="border-b border-line bg-panel px-4 py-3 md:border-b-0 md:border-r last:md:border-r-0">
      <div className="text-xs font-semibold uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-ink">{value}</div>
      {detail ? <div className="mt-1 text-sm text-muted">{detail}</div> : null}
    </div>
  );
}
