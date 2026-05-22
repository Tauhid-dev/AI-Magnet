"use client";

import { useEffect, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type { PortalLead } from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

export default function LeadsPage() {
  const [leads, setLeads] = useState<PortalLead[]>([]);
  const [updatingLeadId, setUpdatingLeadId] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      return;
    }
    portalApi.leads(token).then(setLeads);
  }, []);

  async function updateStatus(leadId: string, status: string) {
    const token = getToken();
    if (!token || !status) {
      return;
    }
    setUpdatingLeadId(leadId);
    try {
      const updatedLead = await portalApi.updateLeadStatus(token, leadId, status);
      setLeads((current) =>
        current.map((lead) => (lead.id === updatedLead.id ? updatedLead : lead))
      );
    } finally {
      setUpdatingLeadId(null);
    }
  }

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
              <th className="px-4 py-3">Notification</th>
              <th className="px-4 py-3">Update</th>
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
                <td className="px-4 py-3">
                  <div className="space-y-2">
                    <StatusPill value={lead.status} />
                    {lead.qualification_reason ? (
                      <div className="max-w-52 text-xs text-muted">{lead.qualification_reason}</div>
                    ) : null}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="space-y-2">
                    <StatusPill value={lead.notification_status} />
                    {lead.last_notified_at ? (
                      <div className="text-xs text-muted">
                        {new Date(lead.last_notified_at).toLocaleString()}
                      </div>
                    ) : null}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <select
                    className="w-36 rounded-md border border-line bg-white px-2 py-2 text-sm text-ink"
                    defaultValue=""
                    disabled={updatingLeadId === lead.id}
                    onChange={(event) => {
                      const value = event.target.value;
                      event.currentTarget.value = "";
                      updateStatus(lead.id, value);
                    }}
                  >
                    <option value="">Set status</option>
                    <option value="contacted">Contacted</option>
                    <option value="closed">Closed</option>
                    <option value="disqualified">Disqualified</option>
                  </select>
                </td>
              </tr>
            ))}
            {leads.length === 0 ? (
              <tr>
                <td className="px-4 py-5 text-muted" colSpan={6}>No leads yet.</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
