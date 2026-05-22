"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "../../../components/AdminShell";
import { StatusPill } from "../../../components/StatusPill";
import { adminApi } from "../../../lib/api/client";
import type { AdminHealth } from "../../../lib/api/types";
import { getAdminToken } from "../../../lib/auth/admin-session";

export default function AdminHealthPage() {
  const [health, setHealth] = useState<AdminHealth | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAdminToken();
    if (!token) {
      return;
    }
    adminApi
      .health(token)
      .then(setHealth)
      .catch(() => setError("Could not load health."));
  }, []);

  return (
    <AdminShell>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">System health</h1>
          <p className="text-sm text-muted">Current backend service and database status.</p>
        </div>
        {health && <StatusPill value={health.status} />}
      </div>
      {error && <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <section className="mt-6 rounded-md border border-line bg-panel">
        <div className="grid gap-2 px-4 py-3 text-sm md:grid-cols-4">
          <div>
            <div className="text-muted">Database</div>
            <div className="font-semibold">{health?.database ?? "-"}</div>
          </div>
          <div>
            <div className="text-muted">App version</div>
            <div className="font-semibold">{health?.app_version ?? "-"}</div>
          </div>
          <div>
            <div className="text-muted">Environment</div>
            <div className="font-semibold">{health?.environment ?? "-"}</div>
          </div>
          <div>
            <div className="text-muted">Status</div>
            <div className="font-semibold">{health?.status ?? "-"}</div>
          </div>
        </div>
      </section>
    </AdminShell>
  );
}
