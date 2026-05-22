"use client";

import { useEffect, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type { PortalLead } from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

export default function LeadsPage() {
  const [leads, setLeads] = useState<PortalLead[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      return;
    }
    portalApi.leads(token).then(setLeads);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Leads</h1>
        <p className="mt-1 text-sm text-muted">Captured enquiries for the current tenant.</p>
      </div>
      <div className="overflow-hidden rounded-lg border border-line bg-panel">
        <table className="w-full border-collapse text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-muted">
            <tr>
              <th className="px-4 py-3">Customer</th>
              <th className="px-4 py-3">Job</th>
              <th className="px-4 py-3">Contact</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {leads.map((lead) => (
              <tr key={lead.id}>
                <td className="px-4 py-3">
                  <div className="font-medium">{lead.customer_name || "Unknown"}</div>
                  <div className="text-muted">{lead.suburb || "-"}</div>
                </td>
                <td className="px-4 py-3">
                  <div>{lead.job_type || "-"}</div>
                  <div className="text-muted">{lead.urgency || "-"}</div>
                </td>
                <td className="px-4 py-3">
                  <div>{lead.customer_phone || "-"}</div>
                  <div className="text-muted">{lead.customer_email || "-"}</div>
                </td>
                <td className="px-4 py-3"><StatusPill value={lead.status} /></td>
              </tr>
            ))}
            {leads.length === 0 ? (
              <tr>
                <td className="px-4 py-5 text-muted" colSpan={4}>No leads yet.</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
