type StatusPillProps = {
  value: string;
};

const styles: Record<string, string> = {
  active: "border-success/20 bg-success/10 text-success",
  ingested: "border-success/20 bg-success/10 text-success",
  open: "border-accent/20 bg-accent/10 text-accent",
  new: "border-accent/20 bg-accent/10 text-accent",
  failed: "border-red-200 bg-red-50 text-red-700",
  revoked: "border-red-200 bg-red-50 text-red-700",
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
