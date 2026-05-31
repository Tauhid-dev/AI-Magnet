type StatusPillProps = {
  value: string;
};

const styles: Record<string, string> = {
  active: "border-emerald-200 bg-emerald-50 text-emerald-700",
  ingested: "border-emerald-200 bg-emerald-50 text-emerald-700",
  complete: "border-emerald-200 bg-emerald-50 text-emerald-700",
  completed: "border-emerald-200 bg-emerald-50 text-emerald-700",
  open: "border-blue-200 bg-blue-50 text-blue-700",
  new: "border-blue-200 bg-blue-50 text-blue-700",
  needs_info: "border-amber-200 bg-amber-50 text-amber-800",
  qualified: "border-blue-200 bg-blue-50 text-blue-700",
  notified: "border-emerald-200 bg-emerald-50 text-emerald-700",
  contacted: "border-blue-200 bg-blue-50 text-blue-700",
  closed: "border-emerald-200 bg-emerald-50 text-emerald-700",
  disqualified: "border-slate-200 bg-slate-100 text-slate-700",
  not_queued: "border-slate-200 bg-slate-100 text-slate-700",
  queued: "border-blue-200 bg-blue-50 text-blue-700",
  sent: "border-emerald-200 bg-emerald-50 text-emerald-700",
  retry_scheduled: "border-amber-200 bg-amber-50 text-amber-800",
  failed: "border-red-200 bg-red-50 text-red-700",
  revoked: "border-red-200 bg-red-50 text-red-700",
  suspended: "border-amber-200 bg-amber-50 text-amber-800",
  inactive: "border-slate-200 bg-slate-100 text-slate-700",
  paused: "border-amber-200 bg-amber-50 text-amber-800",
  ok: "border-emerald-200 bg-emerald-50 text-emerald-700",
  healthy: "border-emerald-200 bg-emerald-50 text-emerald-700",
  degraded: "border-amber-200 bg-amber-50 text-amber-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  blocked: "border-red-200 bg-red-50 text-red-700",
  not_configured: "border-slate-200 bg-slate-100 text-slate-700"
};

export function StatusPill({ value }: StatusPillProps) {
  const normalized = value.toLowerCase();
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-semibold capitalize ${styles[normalized] || "border-line bg-white text-muted"}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}
