type StatusPillProps = {
  value: string;
};

const styles: Record<string, string> = {
  active: "border-success/20 bg-success/10 text-success",
  ingested: "border-success/20 bg-success/10 text-success",
  open: "border-accent/20 bg-accent/10 text-accent",
  new: "border-accent/20 bg-accent/10 text-accent",
  needs_info: "border-orange-200 bg-orange-50 text-orange-700",
  qualified: "border-blue-200 bg-blue-50 text-blue-700",
  notified: "border-success/20 bg-success/10 text-success",
  contacted: "border-blue-200 bg-blue-50 text-blue-700",
  closed: "border-success/20 bg-success/10 text-success",
  disqualified: "border-slate-200 bg-slate-100 text-slate-700",
  not_queued: "border-slate-200 bg-slate-100 text-slate-700",
  queued: "border-blue-200 bg-blue-50 text-blue-700",
  sent: "border-success/20 bg-success/10 text-success",
  retry_scheduled: "border-orange-200 bg-orange-50 text-orange-700",
  failed: "border-red-200 bg-red-50 text-red-700",
  revoked: "border-red-200 bg-red-50 text-red-700",
  suspended: "border-orange-200 bg-orange-50 text-orange-700",
  inactive: "border-slate-200 bg-slate-100 text-slate-700",
  ok: "border-success/20 bg-success/10 text-success",
  degraded: "border-orange-200 bg-orange-50 text-orange-700",
  not_configured: "border-slate-200 bg-slate-100 text-slate-700"
};

export function StatusPill({ value }: StatusPillProps) {
  const normalized = value.toLowerCase();
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-semibold ${styles[normalized] || "border-line bg-white text-muted"}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}
