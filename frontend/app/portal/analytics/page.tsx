"use client";

import { useEffect, useState } from "react";
import { MetricCard } from "../../../components/MetricCard";
import { portalApi } from "../../../lib/api/client";
import type { AnalyticsBreakdown, PortalAnalytics } from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<PortalAnalytics | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      return;
    }
    portalApi.analytics(token).then(setAnalytics);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Analytics</h1>
        <p className="mt-1 text-sm text-muted">Tenant usage and operational totals.</p>
      </div>
      <section className="grid overflow-hidden rounded-lg border border-line bg-panel md:grid-cols-3">
        <MetricCard
          label="Ingested docs"
          value={analytics?.documents_ingested ?? "-"}
          detail={`${analytics?.documents_total ?? "-"} total`}
        />
        <MetricCard
          label="Open chats"
          value={analytics?.open_conversations ?? "-"}
          detail={`${analytics?.conversations_total ?? "-"} total`}
        />
        <MetricCard
          label="Qualified leads"
          value={analytics?.leads_qualified ?? "-"}
          detail={`${analytics?.leads_total ?? "-"} total`}
        />
        <MetricCard
          label="AI responses"
          value={analytics?.ai_responses_total ?? "-"}
          detail={`${analytics?.messages_total ?? "-"} messages`}
        />
        <MetricCard
          label="Lead emails sent"
          value={analytics?.lead_notifications_sent ?? "-"}
          detail={`${analytics?.leads_notified ?? "-"} notified leads`}
        />
        <MetricCard
          label="Usage events"
          value={analytics?.usage_events_total ?? "-"}
          detail={`${analytics?.widget_status ?? "not_configured"} widget`}
        />
      </section>
      <section className="grid gap-4 lg:grid-cols-3">
        <BreakdownPanel title="Lead status" items={analytics?.lead_status_counts || []} />
        <BreakdownPanel title="Document status" items={analytics?.document_status_counts || []} />
        <BreakdownPanel title="Usage events" items={analytics?.usage_event_counts || []} />
      </section>
      <section className="rounded-lg border border-line bg-panel p-4">
        <h2 className="font-semibold">Usage events</h2>
        <div className="mt-3 divide-y divide-line">
          {(analytics?.recent_usage || []).map((event) => (
            <div key={`${event.event_type}-${event.created_at}`} className="grid gap-2 py-3 text-sm md:grid-cols-[220px_1fr_190px]">
              <div className="font-medium">{event.event_type}</div>
              <div className="text-muted">{event.event_source || "-"}</div>
              <div className="text-muted">{new Date(event.created_at).toLocaleString()}</div>
            </div>
          ))}
          {analytics?.recent_usage.length === 0 ? <div className="py-3 text-sm text-muted">No usage events yet.</div> : null}
        </div>
      </section>
    </div>
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
