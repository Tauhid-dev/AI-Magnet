"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "../../components/AdminShell";
import { MetricCard } from "../../components/MetricCard";
import { StatusPill } from "../../components/StatusPill";
import { adminApi } from "../../lib/api/client";
import type { AdminHealth, AdminTenantSummary, AdminUsageOverview } from "../../lib/api/types";
import { getAdminToken } from "../../lib/auth/admin-session";

export default function AdminOverviewPage() {
  const [usage, setUsage] = useState<AdminUsageOverview | null>(null);
  const [health, setHealth] = useState<AdminHealth | null>(null);
  const [tenants, setTenants] = useState<AdminTenantSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAdminToken();
    if (!token) {
      return;
    }
    Promise.all([adminApi.usage(token), adminApi.health(token), adminApi.tenants(token)])
      .then(([usageData, healthData, tenantData]) => {
        setUsage(usageData);
        setHealth(healthData);
        setTenants(tenantData.slice(0, 5));
      })
      .catch(() => setError("Could not load admin overview."));
  }, []);

  return (
    <AdminShell>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Platform overview</h1>
          <p className="text-sm text-muted">Tenant, usage, and health snapshot.</p>
        </div>
        {health && <StatusPill value={health.status} />}
      </div>
      {error && <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <section className="mt-6 grid gap-4 md:grid-cols-4">
        <MetricCard label="Tenants" value={usage?.tenants_total ?? "-"} />
        <MetricCard label="Active" value={usage?.active_tenants ?? "-"} />
        <MetricCard label="Conversations" value={usage?.conversations_total ?? "-"} />
        <MetricCard label="Leads" value={usage?.leads_total ?? "-"} />
      </section>
      <section className="mt-6 rounded-md border border-line bg-panel">
        <div className="border-b border-line px-4 py-3">
          <h2 className="font-semibold">Recent tenants</h2>
        </div>
        <div className="divide-y divide-line">
          {tenants.map((tenant) => (
            <div key={tenant.id} className="grid gap-2 px-4 py-3 md:grid-cols-4">
              <div className="font-medium">{tenant.name}</div>
              <div className="text-sm text-muted">{tenant.slug}</div>
              <StatusPill value={tenant.status} />
              <div className="text-sm text-muted">
                {tenant.metrics.conversations_total} conversations
              </div>
            </div>
          ))}
          {tenants.length === 0 && (
            <div className="px-4 py-6 text-sm text-muted">No tenants available.</div>
          )}
        </div>
      </section>
    </AdminShell>
  );
}
