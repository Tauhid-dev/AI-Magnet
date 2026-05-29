"use client";

import { useEffect, useMemo, useState } from "react";
import { AdminShell } from "../../../components/AdminShell";
import { StatusPill } from "../../../components/StatusPill";
import { adminApi } from "../../../lib/api/client";
import type { AdminTenantSummary, BillingPlan, TenantSubscription } from "../../../lib/api/types";
import { getAdminToken } from "../../../lib/auth/admin-session";

const subscriptionStatuses = ["trialing", "active", "past_due", "paused", "canceled"];

export default function AdminBillingPage() {
  const [tenants, setTenants] = useState<AdminTenantSummary[]>([]);
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [selectedTenantId, setSelectedTenantId] = useState("");
  const [subscription, setSubscription] = useState<TenantSubscription | null>(null);
  const [planCode, setPlanCode] = useState("");
  const [status, setStatus] = useState("trialing");
  const [billingContactEmail, setBillingContactEmail] = useState("");
  const [manualReference, setManualReference] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const selectedTenant = useMemo(
    () => tenants.find((tenant) => tenant.id === selectedTenantId) || null,
    [selectedTenantId, tenants]
  );

  useEffect(() => {
    const token = getAdminToken();
    if (!token) {
      return;
    }
    Promise.all([adminApi.tenants(token), adminApi.billingPlans(token)])
      .then(([tenantRows, planRows]) => {
        setTenants(tenantRows);
        setPlans(planRows);
        setSelectedTenantId(tenantRows[0]?.id || "");
        setPlanCode(planRows[0]?.code || "");
      })
      .catch(() => setError("Could not load billing controls."));
  }, []);

  useEffect(() => {
    const token = getAdminToken();
    if (!token || !selectedTenantId) {
      return;
    }
    adminApi
      .tenantSubscription(token, selectedTenantId)
      .then((nextSubscription) => {
        setSubscription(nextSubscription);
        if (nextSubscription) {
          setPlanCode(nextSubscription.plan_code);
          setStatus(nextSubscription.status);
          setBillingContactEmail(nextSubscription.billing_contact_email || "");
          setManualReference(nextSubscription.manual_reference || "");
          setNotes(nextSubscription.notes || "");
        } else {
          setPlanCode(plans[0]?.code || "");
          setStatus("trialing");
          setBillingContactEmail("");
          setManualReference("");
          setNotes("");
        }
      })
      .catch(() => setError("Could not load tenant subscription."));
  }, [plans, selectedTenantId]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getAdminToken();
    if (!token || !selectedTenantId) {
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const updated = await adminApi.updateTenantSubscription(token, selectedTenantId, {
        plan_code: planCode,
        status,
        billing_contact_email: billingContactEmail || null,
        manual_reference: manualReference || null,
        notes: notes || null
      });
      setSubscription(updated);
    } catch {
      setError("Could not save subscription.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <AdminShell>
      <div>
        <h1 className="text-2xl font-semibold">Billing</h1>
        <p className="text-sm text-muted">
          Manual paid-beta entitlements, status controls, and plan limits.
        </p>
      </div>
      {error && <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <section className="mt-6 grid gap-4 lg:grid-cols-[320px_1fr]">
        <div className="rounded-lg border border-line bg-panel p-4">
          <h2 className="text-sm font-semibold">Tenant</h2>
          <select
            className="mt-3 w-full rounded-md border border-line px-3 py-2"
            value={selectedTenantId}
            onChange={(event) => setSelectedTenantId(event.target.value)}
          >
            {tenants.map((tenant) => (
              <option key={tenant.id} value={tenant.id}>
                {tenant.name}
              </option>
            ))}
          </select>
          {selectedTenant && (
            <div className="mt-4 space-y-2 text-sm">
              <div className="font-medium">{selectedTenant.slug}</div>
              <StatusPill value={selectedTenant.status} />
              <div className="text-muted">
                {selectedTenant.metrics.conversations_total} chats, {selectedTenant.metrics.leads_total} leads
              </div>
            </div>
          )}
        </div>
        <form onSubmit={handleSubmit} className="rounded-lg border border-line bg-panel p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-sm font-semibold">Subscription</h2>
            {subscription ? <StatusPill value={subscription.status} /> : <StatusPill value="not_configured" />}
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="text-sm">
              <span className="font-medium">Plan</span>
              <select
                className="mt-1 w-full rounded-md border border-line px-3 py-2"
                value={planCode}
                onChange={(event) => setPlanCode(event.target.value)}
              >
                {plans.map((plan) => (
                  <option key={plan.code} value={plan.code}>
                    {plan.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="font-medium">Status</span>
              <select
                className="mt-1 w-full rounded-md border border-line px-3 py-2"
                value={status}
                onChange={(event) => setStatus(event.target.value)}
              >
                {subscriptionStatuses.map((item) => (
                  <option key={item} value={item}>
                    {item.replaceAll("_", " ")}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              <span className="font-medium">Billing contact</span>
              <input
                className="mt-1 w-full rounded-md border border-line px-3 py-2"
                value={billingContactEmail}
                onChange={(event) => setBillingContactEmail(event.target.value)}
                placeholder="billing@example.com"
              />
            </label>
            <label className="text-sm">
              <span className="font-medium">Manual reference</span>
              <input
                className="mt-1 w-full rounded-md border border-line px-3 py-2"
                value={manualReference}
                onChange={(event) => setManualReference(event.target.value)}
                placeholder="invoice or approval reference"
              />
            </label>
            <label className="text-sm md:col-span-2">
              <span className="font-medium">Internal notes</span>
              <textarea
                className="mt-1 min-h-24 w-full rounded-md border border-line px-3 py-2"
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
              />
            </label>
          </div>
          <button
            type="submit"
            disabled={saving || !selectedTenantId || !planCode}
            className="mt-4 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
          >
            {saving ? "Saving" : "Save subscription"}
          </button>
        </form>
      </section>
      <section className="mt-6 overflow-hidden rounded-lg border border-line bg-panel">
        <div className="border-b border-line px-4 py-3">
          <h2 className="font-semibold">Plan catalog</h2>
        </div>
        <div className="divide-y divide-line">
          {plans.map((plan) => (
            <div key={plan.code} className="grid gap-3 px-4 py-4 text-sm lg:grid-cols-[1fr_140px_140px_140px]">
              <div>
                <div className="font-medium">{plan.name}</div>
                <div className="mt-1 text-muted">{plan.description}</div>
              </div>
              <div>
                <div className="text-muted">Price</div>
                <div className="font-semibold">{formatMoney(plan.monthly_price_cents, plan.currency)}</div>
              </div>
              <div>
                <div className="text-muted">AI budget</div>
                <div className="font-semibold">${(plan.monthly_budget_cents / 100).toFixed(2)}</div>
              </div>
              <div>
                <div className="text-muted">Support</div>
                <div className="font-semibold">{plan.support_level}</div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </AdminShell>
  );
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
