"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type {
  BackgroundJob,
  PortalAnalytics,
  PortalBusinessProfile,
  PortalDocument,
  PortalWebsiteSource,
  PortalWidget
} from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

type ProfileForm = {
  business_name: string;
  business_email: string;
  business_phone: string;
  website_url: string;
};

type ChecklistItem = {
  label: string;
  complete: boolean;
  href: string;
  action: string;
};

export default function OnboardingPage() {
  const [profile, setProfile] = useState<PortalBusinessProfile | null>(null);
  const [analytics, setAnalytics] = useState<PortalAnalytics | null>(null);
  const [documents, setDocuments] = useState<PortalDocument[]>([]);
  const [sources, setSources] = useState<PortalWebsiteSource[]>([]);
  const [widget, setWidget] = useState<PortalWidget | null>(null);
  const [jobs, setJobs] = useState<BackgroundJob[]>([]);
  const [form, setForm] = useState<ProfileForm>({
    business_name: "",
    business_email: "",
    business_phone: "",
    website_url: ""
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const loadOnboarding = useCallback(async () => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const [
        nextProfile,
        nextAnalytics,
        nextDocuments,
        nextSources,
        nextWidget,
        nextJobs
      ] = await Promise.all([
        portalApi.profile(token),
        portalApi.analytics(token),
        portalApi.documents(token),
        portalApi.websiteSources(token),
        portalApi.widget(token),
        portalApi.jobs(token)
      ]);
      setProfile(nextProfile);
      setAnalytics(nextAnalytics);
      setDocuments(nextDocuments);
      setSources(nextSources);
      setWidget(nextWidget);
      setJobs(nextJobs);
      setForm({
        business_name: nextProfile.business_name || nextProfile.tenant_name,
        business_email: nextProfile.business_email || "",
        business_phone: nextProfile.business_phone || "",
        website_url: nextProfile.website_url || ""
      });
    } catch {
      setError("Setup status could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOnboarding();
  }, [loadOnboarding]);

  const checklist = useMemo<ChecklistItem[]>(() => {
    const profileComplete = Boolean(
      form.business_name.trim() && (profile?.website_url || form.website_url.trim())
    );
    const knowledgeAdded = documents.length > 0 || sources.length > 0;
    const indexedKnowledge = Boolean(analytics && analytics.documents_ingested > 0);
    const agentTested = Boolean(
      analytics?.recent_usage.some((event) => event.event_type === "agent_sandbox_tested")
    );
    const widgetConfigured = Boolean(
      widget?.status === "active" && widget.allowed_origins.length > 0
    );
    return [
      {
        label: "Business profile",
        complete: profileComplete,
        href: "/portal/onboarding",
        action: "Profile"
      },
      {
        label: "Knowledge source",
        complete: knowledgeAdded,
        href: "/portal/documents",
        action: "Knowledge"
      },
      {
        label: "Indexed knowledge",
        complete: indexedKnowledge,
        href: "/portal/documents",
        action: "Jobs"
      },
      {
        label: "Agent test",
        complete: agentTested,
        href: "/portal/agent",
        action: "Test"
      },
      {
        label: "Widget install",
        complete: widgetConfigured,
        href: "/portal/widget",
        action: "Widget"
      }
    ];
  }, [analytics, documents.length, form.business_name, form.website_url, profile, sources.length, widget]);

  const completionCount = checklist.filter((item) => item.complete).length;
  const completionPercent = Math.round((completionCount / checklist.length) * 100);
  const activeJobs = jobs.filter((job) =>
    ["queued", "running", "retry_scheduled"].includes(job.status)
  );

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getToken();
    if (!token) {
      return;
    }
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const nextProfile = await portalApi.updateProfile(token, {
        business_name: form.business_name,
        business_email: form.business_email || null,
        business_phone: form.business_phone || null,
        website_url: form.website_url || null
      });
      setProfile(nextProfile);
      setForm({
        business_name: nextProfile.business_name || nextProfile.tenant_name,
        business_email: nextProfile.business_email || "",
        business_phone: nextProfile.business_phone || "",
        website_url: nextProfile.website_url || ""
      });
      setSaved(true);
    } catch {
      setError("Business profile could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Setup</h1>
          <p className="mt-1 text-sm text-muted">
            Business profile, knowledge readiness, agent test, and widget controls.
          </p>
        </div>
        <div className="min-w-48 rounded-lg border border-line bg-panel p-3">
          <div className="text-sm font-semibold text-muted">Readiness</div>
          <div className="mt-2 flex items-center gap-3">
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-accent"
                style={{ width: `${completionPercent}%` }}
              />
            </div>
            <div className="text-sm font-semibold">{completionPercent}%</div>
          </div>
        </div>
      </div>

      {error ? (
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      {loading ? (
        <div className="rounded-lg border border-line bg-panel p-4 text-sm text-muted">
          Loading setup status...
        </div>
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
          <section className="rounded-lg border border-line bg-panel p-4">
            <div className="mb-4">
              <h2 className="text-lg font-semibold">Business profile</h2>
              <p className="mt-1 text-sm text-muted">
                {profile?.tenant_name || "Current tenant"}
              </p>
            </div>
            <form className="grid gap-4 md:grid-cols-2" onSubmit={saveProfile}>
              <label className="text-sm font-semibold text-muted">
                Business name
                <input
                  className="mt-2 w-full rounded-md border border-line px-3 py-2 text-ink"
                  value={form.business_name}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      business_name: event.target.value
                    }))
                  }
                  required
                />
              </label>
              <label className="text-sm font-semibold text-muted">
                Booking email
                <input
                  className="mt-2 w-full rounded-md border border-line px-3 py-2 text-ink"
                  type="email"
                  value={form.business_email}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      business_email: event.target.value
                    }))
                  }
                />
              </label>
              <label className="text-sm font-semibold text-muted">
                Phone
                <input
                  className="mt-2 w-full rounded-md border border-line px-3 py-2 text-ink"
                  value={form.business_phone}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      business_phone: event.target.value
                    }))
                  }
                />
              </label>
              <label className="text-sm font-semibold text-muted">
                Website
                <input
                  className="mt-2 w-full rounded-md border border-line px-3 py-2 text-ink"
                  type="url"
                  value={form.website_url}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      website_url: event.target.value
                    }))
                  }
                  placeholder="https://example.com"
                />
              </label>
              <div className="flex flex-wrap items-center gap-3 md:col-span-2">
                <button
                  className="rounded-md bg-accent px-4 py-2 font-semibold text-white disabled:opacity-60"
                  disabled={saving}
                >
                  Save profile
                </button>
                {saved ? <span className="text-sm text-green-700">Saved</span> : null}
              </div>
            </form>
          </section>

          <section className="rounded-lg border border-line bg-panel p-4">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold">Launch checklist</h2>
              <span className="text-sm font-semibold text-muted">
                {completionCount}/{checklist.length}
              </span>
            </div>
            <div className="space-y-3">
              {checklist.map((item) => (
                <div
                  className="flex items-center justify-between gap-3 rounded-md border border-line p-3"
                  key={item.label}
                >
                  <div>
                    <div className="font-semibold">{item.label}</div>
                    <div className="mt-1">
                      <StatusPill value={item.complete ? "complete" : "pending"} />
                    </div>
                  </div>
                  <Link
                    className="rounded-md border border-line px-3 py-2 text-sm font-semibold text-ink"
                    href={item.href}
                  >
                    {item.action}
                  </Link>
                </div>
              ))}
            </div>
          </section>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="rounded-lg border border-line bg-panel p-4">
          <h2 className="font-semibold">Knowledge</h2>
          <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
            <Metric label="Documents" value={documents.length} />
            <Metric label="Sources" value={sources.length} />
            <Metric label="Indexed" value={analytics?.documents_ingested || 0} />
            <Metric label="Failed" value={analytics?.documents_failed || 0} />
          </div>
        </section>
        <section className="rounded-lg border border-line bg-panel p-4">
          <h2 className="font-semibold">Active jobs</h2>
          <div className="mt-3 space-y-2">
            {activeJobs.slice(0, 4).map((job) => (
              <div className="flex items-center justify-between gap-3 text-sm" key={job.id}>
                <span className="truncate">{job.job_type}</span>
                <StatusPill value={job.status} />
              </div>
            ))}
            {activeJobs.length === 0 ? (
              <div className="text-sm text-muted">No active indexing jobs.</div>
            ) : null}
          </div>
        </section>
        <section className="rounded-lg border border-line bg-panel p-4">
          <h2 className="font-semibold">Widget</h2>
          <div className="mt-3 space-y-3 text-sm">
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted">Status</span>
              <StatusPill value={widget?.status || "not_configured"} />
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted">Allowed domains</span>
              <span className="font-semibold">{widget?.allowed_origins.length || 0}</span>
            </div>
            <Link className="inline-block text-sm font-semibold text-accent" href="/portal/widget">
              Widget settings
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md bg-slate-50 p-3">
      <div className="text-xs font-semibold uppercase text-muted">{label}</div>
      <div className="mt-1 text-xl font-semibold">{value}</div>
    </div>
  );
}
