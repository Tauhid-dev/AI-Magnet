"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "../../../components/AdminShell";
import { MetricCard } from "../../../components/MetricCard";
import { adminApi } from "../../../lib/api/client";
import type { AdminUsageOverview, AnalyticsBreakdown } from "../../../lib/api/types";
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
        <MetricCard
          label="Tenants"
          value={usage?.tenants_total ?? "-"}
          detail={`${usage?.active_tenants ?? "-"} active`}
        />
        <MetricCard
          label="Documents"
          value={usage?.documents_total ?? "-"}
          detail={`${usage?.documents_ingested ?? "-"} ingested`}
        />
        <MetricCard
          label="Qualified leads"
          value={usage?.leads_qualified ?? "-"}
          detail={`${usage?.leads_total ?? "-"} total`}
        />
        <MetricCard label="Conversations" value={usage?.conversations_total ?? "-"} />
        <MetricCard
          label="AI responses"
          value={usage?.ai_responses_total ?? "-"}
          detail={`${usage?.messages_total ?? "-"} messages`}
        />
        <MetricCard
          label="Usage events"
          value={usage?.usage_events_total ?? "-"}
          detail={`${usage?.admin_audit_events_total ?? "-"} audit events`}
        />
        <MetricCard
          label="AI cost"
          value={usage ? `$${(usage.estimated_cost_cents_total / 100).toFixed(2)}` : "-"}
          detail={`${usage?.estimated_tokens_total ?? "-"} est. tokens`}
        />
        <MetricCard
          label="Quota alerts"
          value={usage?.quota_warning_tenants ?? "-"}
          detail={`${usage?.quota_blocked_tenants ?? "-"} blocked tenants`}
        />
        <MetricCard
          label="Crawl/storage"
          value={usage?.pages_crawled_total ?? "-"}
          detail={`${usage?.storage_mb_total ?? "-"} MB stored`}
        />
      </section>
      <section className="mt-6 grid gap-4 lg:grid-cols-3">
        <BreakdownPanel title="Usage events" items={usage?.usage_event_counts || []} />
        <BreakdownPanel title="Lead status" items={usage?.lead_status_counts || []} />
        <BreakdownPanel title="Document status" items={usage?.document_status_counts || []} />
      </section>
      <section className="mt-6 overflow-hidden rounded-lg border border-line bg-panel">
        <table className="w-full border-collapse text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-muted">
            <tr>
              <th className="px-4 py-3">Tenant</th>
              <th className="px-4 py-3">Docs</th>
              <th className="px-4 py-3">Leads</th>
              <th className="px-4 py-3">Chats</th>
              <th className="px-4 py-3">Messages</th>
              <th className="px-4 py-3">Usage events</th>
              <th className="px-4 py-3">Tokens</th>
              <th className="px-4 py-3">Cost</th>
              <th className="px-4 py-3">Quota</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {(usage?.tenant_usage || []).map((tenant) => (
              <tr key={tenant.tenant_id}>
                <td className="px-4 py-3">
                  <div className="font-medium">{tenant.tenant_name}</div>
                  <div className="text-muted">{tenant.tenant_slug}</div>
                </td>
                <td className="px-4 py-3">{tenant.documents_total}</td>
                <td className="px-4 py-3">{tenant.leads_total}</td>
                <td className="px-4 py-3">{tenant.conversations_total}</td>
                <td className="px-4 py-3">{tenant.messages_total}</td>
                <td className="px-4 py-3">{tenant.usage_events_total}</td>
                <td className="px-4 py-3">{tenant.estimated_tokens}</td>
                <td className="px-4 py-3">${(tenant.estimated_cost_cents / 100).toFixed(2)}</td>
                <td className="px-4 py-3">
                  {tenant.quota_blockers.length > 0 ? (
                    <span className="rounded-full bg-red-50 px-2 py-1 text-xs font-semibold text-red-700">Blocked</span>
                  ) : tenant.quota_warnings.length > 0 ? (
                    <span className="rounded-full bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-700">Warning</span>
                  ) : (
                    <span className="rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700">OK</span>
                  )}
                </td>
              </tr>
            ))}
            {usage?.tenant_usage.length === 0 ? (
              <tr>
                <td className="px-4 py-5 text-muted" colSpan={9}>No tenant usage yet.</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </section>
    </AdminShell>
  );
}

function BreakdownPanel({ title, items }: { title: string; items: AnalyticsBreakdown[] }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-4">
      <h2 className="text-sm font-semibold">{title}</h2>
      <div className="mt-3 space-y-2">
        {items.map((item) => (
          <div key={item.label} className="flex items-center justify-between gap-3 text-sm">
            <span className="text-muted">{item.label.replaceAll("_", " ")}</span>
            <span className="font-semibold">{item.count}</span>
          </div>
        ))}
        {items.length === 0 ? <div className="text-sm text-muted">No data yet.</div> : null}
      </div>
    </section>
  );
}
