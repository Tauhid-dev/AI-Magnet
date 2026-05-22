"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "../../../components/AdminShell";
import { MetricCard } from "../../../components/MetricCard";
import { adminApi } from "../../../lib/api/client";
import type { AdminUsageOverview } from "../../../lib/api/types";
import { getAdminToken } from "../../../lib/auth/admin-session";

export default function AdminUsagePage() {
  const [usage, setUsage] = useState<AdminUsageOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAdminToken();
    if (!token) {
      return;
    }
    adminApi
      .usage(token)
      .then(setUsage)
      .catch(() => setError("Could not load usage."));
  }, []);

  return (
    <AdminShell>
      <div>
        <h1 className="text-2xl font-semibold">Usage</h1>
        <p className="text-sm text-muted">Platform totals for operations and support.</p>
      </div>
      {error && <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <section className="mt-6 grid gap-4 md:grid-cols-3">
        <MetricCard label="Tenants" value={usage?.tenants_total ?? "-"} />
        <MetricCard label="Documents" value={usage?.documents_total ?? "-"} />
        <MetricCard label="Leads" value={usage?.leads_total ?? "-"} />
        <MetricCard label="Conversations" value={usage?.conversations_total ?? "-"} />
        <MetricCard label="Messages" value={usage?.messages_total ?? "-"} />
        <MetricCard label="Usage events" value={usage?.usage_events_total ?? "-"} />
      </section>
    </AdminShell>
  );
}
