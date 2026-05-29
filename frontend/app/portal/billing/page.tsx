"use client";

import { useEffect, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type { BillingPlan, PortalBilling, QuotaMetric } from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

export default function PortalBillingPage() {
  const [billing, setBilling] = useState<PortalBilling | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      return;
    }
    portalApi
      .billing(token)
      .then(setBilling)
      .catch(() => setError("Could not load billing status."));
  }, []);

  const subscription = billing?.subscription;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Billing</h1>
        <p className="mt-1 text-sm text-muted">
          Paid-beta access, plan limits, privacy operations, and support status.
        </p>
      </div>
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <section className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-lg border border-line bg-panel p-4">
          <h2 className="text-sm font-semibold">Subscription</h2>
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted">Status</span>
              {subscription ? <StatusPill value={subscription.status} /> : <StatusPill value="not_configured" />}
            </div>
            <KeyValue label="Plan" value={subscription?.plan_name || "Manual approval pending"} />
            <KeyValue label="Billing mode" value={subscription?.billing_mode || "manual"} />
            <KeyValue label="Price" value={subscription ? formatMoney(subscription.monthly_price_cents, subscription.currency) : "-"} />
            <KeyValue label="Support" value={subscription?.support_level || "-"} />
            <KeyValue label="Period ends" value={formatDate(subscription?.current_period_ends_at)} />
          </div>
        </div>
        <div className="rounded-lg border border-line bg-panel p-4 lg:col-span-2">
          <h2 className="text-sm font-semibold">Paid-beta controls</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <ControlList title="Privacy operations" items={billing?.privacy_operations || []} />
            <ControlList title="Support workflow" items={billing?.support_workflow || []} />
          </div>
          <div className="mt-4 rounded-md border border-line bg-slate-50 p-3 text-sm">
            <div className="font-medium">Payment collection</div>
            <div className="mt-1 text-muted">{billing?.payment_collection || "-"}</div>
          </div>
        </div>
      </section>
      <section className="rounded-lg border border-line bg-panel p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-semibold">Entitlement limits</h2>
            <p className="mt-1 text-sm text-muted">
              Server-enforced usage limits for the current monthly window.
            </p>
          </div>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
            {billing?.paid_beta_status.replaceAll("_", " ") || "loading"}
          </span>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {(billing?.quota_status.metrics || []).map((metric) => (
            <QuotaMeter key={metric.key} metric={metric} />
          ))}
        </div>
        {billing?.quota_status.blocked_reasons.length ? (
          <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
            {billing.quota_status.blocked_reasons.join(", ")}
          </div>
        ) : null}
      </section>
      <section className="overflow-hidden rounded-lg border border-line bg-panel">
        <div className="border-b border-line px-4 py-3">
          <h2 className="font-semibold">Available beta plans</h2>
        </div>
        <div className="divide-y divide-line">
          {(billing?.available_plans || []).map((plan) => (
            <PlanRow key={plan.code} plan={plan} />
          ))}
        </div>
      </section>
    </div>
  );
}

function KeyValue({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-muted">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

function ControlList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-md border border-line p-3">
      <h3 className="text-sm font-semibold">{title}</h3>
      <ul className="mt-2 space-y-2 text-sm text-muted">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function QuotaMeter({ metric }: { metric: QuotaMetric }) {
  return (
    <div className="rounded-md border border-line p-3">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="font-medium">{metric.label}</span>
        <span className={metric.blocked ? "text-red-700" : metric.warning ? "text-amber-700" : "text-muted"}>
          {metric.percent_used.toFixed(1)}%
        </span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className={metric.blocked ? "h-full bg-red-600" : metric.warning ? "h-full bg-amber-500" : "h-full bg-emerald-600"}
          style={{ width: `${Math.min(metric.percent_used, 100)}%` }}
        />
      </div>
      <div className="mt-2 text-xs text-muted">
        {formatMetricValue(metric.used, metric.unit)} of {formatMetricValue(metric.limit, metric.unit)}
      </div>
    </div>
  );
}

function PlanRow({ plan }: { plan: BillingPlan }) {
  return (
    <div className="grid gap-3 px-4 py-4 text-sm md:grid-cols-[1fr_160px_160px]">
      <div>
        <div className="font-medium">{plan.name}</div>
        <div className="mt-1 text-muted">{plan.description}</div>
      </div>
      <div>
        <div className="text-muted">Monthly</div>
        <div className="font-semibold">{formatMoney(plan.monthly_price_cents, plan.currency)}</div>
      </div>
      <div>
        <div className="text-muted">Limits</div>
        <div className="font-semibold">{plan.chat_conversations_limit} chats</div>
      </div>
    </div>
  );
}

function formatMetricValue(value: number, unit: string) {
  const rounded = unit.includes("cents") || unit === "MB" ? value.toFixed(2) : Math.round(value).toString();
  return `${rounded} ${unit}`;
}

function formatMoney(cents: number, currency: string) {
  if (cents === 0) {
    return "$0";
  }
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency
  }).format(cents / 100);
}

function formatDate(value?: string | null) {
  return value ? new Date(value).toLocaleDateString() : "-";
}
