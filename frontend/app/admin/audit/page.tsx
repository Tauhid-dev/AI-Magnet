"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "../../../components/AdminShell";
import { adminApi } from "../../../lib/api/client";
import type { AdminAuditLog } from "../../../lib/api/types";
import { getAdminToken } from "../../../lib/auth/admin-session";

export default function AdminAuditPage() {
  const [auditLogs, setAuditLogs] = useState<AdminAuditLog[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAdminToken();
    if (!token) {
      return;
    }
    adminApi
      .auditLogs(token)
      .then(setAuditLogs)
      .catch(() => setError("Could not load audit logs."));
  }, []);

  return (
    <AdminShell>
      <div>
        <h1 className="text-2xl font-semibold">Audit log</h1>
        <p className="text-sm text-muted">Recent tenant-scoped admin actions.</p>
      </div>
      {error && <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <section className="mt-6 rounded-md border border-line bg-panel">
        <div className="grid gap-2 border-b border-line px-4 py-3 text-sm font-semibold text-muted md:grid-cols-5">
          <div>Action</div>
          <div>Tenant</div>
          <div>Target</div>
          <div>Actor</div>
          <div>Created</div>
        </div>
        <div className="divide-y divide-line">
          {auditLogs.map((event) => (
            <div key={event.id} className="grid gap-2 px-4 py-3 text-sm md:grid-cols-5">
              <div className="font-medium">{event.action}</div>
              <div className="text-muted">{event.tenant_id}</div>
              <div className="text-muted">
                {event.target_type || "-"} {event.target_id || ""}
              </div>
              <div className="text-muted">{event.actor_id || "-"}</div>
              <div className="text-muted">{new Date(event.created_at).toLocaleString()}</div>
            </div>
          ))}
          {auditLogs.length === 0 && (
            <div className="px-4 py-6 text-sm text-muted">No audit events available.</div>
          )}
        </div>
      </section>
    </AdminShell>
  );
}
