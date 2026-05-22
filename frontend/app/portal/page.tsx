"use client";

import { useEffect, useState } from "react";
import { MetricCard } from "../../components/MetricCard";
import { StatusPill } from "../../components/StatusPill";
import { portalApi } from "../../lib/api/client";
import type { PortalAnalytics, PortalWidget } from "../../lib/api/types";
import { getToken } from "../../lib/auth/session";

export default function PortalOverviewPage() {
  const [analytics, setAnalytics] = useState<PortalAnalytics | null>(null);
  const [widget, setWidget] = useState<PortalWidget | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      return;
    }
    Promise.all([portalApi.analytics(token), portalApi.widget(token)]).then(
      ([analyticsResponse, widgetResponse]) => {
        setAnalytics(analyticsResponse);
        setWidget(widgetResponse);
      }
    );
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Overview</h1>
        <p className="mt-1 text-sm text-muted">Today&apos;s tenant workspace snapshot.</p>
      </div>
      <section className="grid overflow-hidden rounded-lg border border-line bg-panel md:grid-cols-4">
        <MetricCard label="Leads" value={analytics?.leads_total ?? "-"} />
        <MetricCard label="Conversations" value={analytics?.conversations_total ?? "-"} />
        <MetricCard label="Knowledge files" value={analytics?.documents_total ?? "-"} />
        <MetricCard label="Messages" value={analytics?.messages_total ?? "-"} />
      </section>
      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-line bg-panel p-4">
          <h2 className="font-semibold">Widget</h2>
          <div className="mt-4 flex items-center justify-between border-t border-line pt-4">
            <span className="text-sm text-muted">Status</span>
            <StatusPill value={widget?.status || "not_configured"} />
          </div>
          <div className="mt-3 flex items-center justify-between">
            <span className="text-sm text-muted">Key prefix</span>
            <span className="font-mono text-sm">{widget?.key_prefix || "-"}</span>
          </div>
        </div>
        <div className="rounded-lg border border-line bg-panel p-4">
          <h2 className="font-semibold">Recent usage</h2>
          <div className="mt-3 divide-y divide-line">
            {(analytics?.recent_usage || []).slice(0, 5).map((event) => (
              <div key={`${event.event_type}-${event.created_at}`} className="py-2 text-sm">
                <div className="font-medium">{event.event_type}</div>
                <div className="text-muted">{new Date(event.created_at).toLocaleString()}</div>
              </div>
            ))}
            {analytics?.recent_usage.length === 0 ? <div className="py-3 text-sm text-muted">No usage yet.</div> : null}
          </div>
        </div>
      </section>
    </div>
  );
}
