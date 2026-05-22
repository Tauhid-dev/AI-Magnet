"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { AdminShell } from "../../../../components/AdminShell";
import { MetricCard } from "../../../../components/MetricCard";
import { StatusPill } from "../../../../components/StatusPill";
import { adminApi } from "../../../../lib/api/client";
import type {
  AdminSupportContext,
  AdminTenantDetail
} from "../../../../lib/api/types";
import { getAdminToken } from "../../../../lib/auth/admin-session";

export default function AdminTenantDetailPage() {
  const params = useParams<{ tenantId: string }>();
  const tenantId = params.tenantId;
  const [tenant, setTenant] = useState<AdminTenantDetail | null>(null);
  const [support, setSupport] = useState<AdminSupportContext | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadTenant = useCallback(async () => {
    const token = getAdminToken();
    if (!token) {
      return;
    }
    const [detail, context] = await Promise.all([
      adminApi.tenant(token, tenantId),
      adminApi.supportContext(token, tenantId)
    ]);
    setTenant(detail);
    setSupport(context);
  }, [tenantId]);

  useEffect(() => {
    loadTenant().catch(() => setError("Could not load tenant."));
  }, [loadTenant]);

  async function updateStatus(status: string) {
    const token = getAdminToken();
    if (!token) {
      return;
    }
    try {
      setTenant(await adminApi.updateTenantStatus(token, tenantId, status));
      await loadTenant();
    } catch {
      setError("Could not update tenant status.");
    }
  }

  return (
    <AdminShell>
      {error && <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      {!tenant ? (
        <div className="text-sm text-muted">Loading tenant...</div>
      ) : (
        <>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-semibold">{tenant.name}</h1>
              <p className="text-sm text-muted">{tenant.slug}</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <StatusPill value={tenant.status} />
              <button
                type="button"
                className="rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold"
                onClick={() => updateStatus("active")}
              >
                Activate
              </button>
              <button
                type="button"
                className="rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold"
                onClick={() => updateStatus("suspended")}
              >
                Suspend
              </button>
            </div>
          </div>
          <section className="mt-6 grid gap-4 md:grid-cols-4">
            <MetricCard label="Business users" value={tenant.metrics.users_total} />
            <MetricCard label="Documents" value={tenant.metrics.documents_total} />
            <MetricCard label="Leads" value={tenant.metrics.leads_total} />
            <MetricCard label="Messages" value={tenant.metrics.messages_total} />
          </section>
          <section className="mt-6 grid gap-4 lg:grid-cols-2">
            <div className="rounded-md border border-line bg-panel">
              <div className="border-b border-line px-4 py-3 font-semibold">Businesses</div>
              <div className="divide-y divide-line">
                {tenant.businesses.map((business) => (
                  <div key={business.id} className="px-4 py-3 text-sm">
                    <div className="font-medium">{business.name}</div>
                    <div className="text-muted">{business.email || "No email"}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-md border border-line bg-panel">
              <div className="border-b border-line px-4 py-3 font-semibold">Business users</div>
              <div className="divide-y divide-line">
                {tenant.users.map((user) => (
                  <div key={user.id} className="grid gap-2 px-4 py-3 text-sm md:grid-cols-3">
                    <div className="font-medium">{user.email}</div>
                    <div className="text-muted">{user.role}</div>
                    <StatusPill value={user.status} />
                  </div>
                ))}
              </div>
            </div>
          </section>
          <section className="mt-6 rounded-md border border-line bg-panel">
            <div className="border-b border-line px-4 py-3 font-semibold">
              Limited support context
            </div>
            <div className="grid gap-4 p-4 lg:grid-cols-2">
              <div>
                <h2 className="font-semibold">Recent leads</h2>
                <div className="mt-2 divide-y divide-line rounded-md border border-line">
                  {support?.recent_leads.map((lead) => (
                    <div key={lead.id} className="px-3 py-2 text-sm">
                      <div className="font-medium">{lead.job_type || "Unclassified job"}</div>
                      <div className="text-muted">
                        {lead.suburb || "No suburb"} · {lead.urgency || "No urgency"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h2 className="font-semibold">Recent conversations</h2>
                <div className="mt-2 divide-y divide-line rounded-md border border-line">
                  {support?.recent_conversations.map((conversation) => (
                    <div key={conversation.id} className="px-3 py-2 text-sm">
                      <div className="font-medium">{conversation.status}</div>
                      <div className="text-muted">
                        {conversation.source} · {conversation.message_count} messages
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        </>
      )}
    </AdminShell>
  );
}
