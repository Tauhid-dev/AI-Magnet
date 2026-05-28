"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AdminShell } from "../../../components/AdminShell";
import { StatusPill } from "../../../components/StatusPill";
import { adminApi } from "../../../lib/api/client";
import type { AdminTenantSummary } from "../../../lib/api/types";
import { getAdminToken } from "../../../lib/auth/admin-session";

export default function AdminTenantsPage() {
  const [tenants, setTenants] = useState<AdminTenantSummary[]>([]);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [ownerEmail, setOwnerEmail] = useState("");
  const [ownerPassword, setOwnerPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadTenants() {
    const token = getAdminToken();
    if (!token) {
      return;
    }
    setTenants(await adminApi.tenants(token));
  }

  useEffect(() => {
    loadTenants().catch(() => setError("Could not load tenants."));
  }, []);

  async function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getAdminToken();
    if (!token) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await adminApi.createTenant(token, {
        name,
        slug,
        owner_email: ownerEmail || undefined,
        business_email: ownerEmail || undefined,
        owner_password: ownerPassword || undefined
      });
      setName("");
      setSlug("");
      setOwnerEmail("");
      setOwnerPassword("");
      await loadTenants();
    } catch {
      setError("Could not create tenant.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AdminShell>
      <div>
        <h1 className="text-2xl font-semibold">Tenants</h1>
        <p className="text-sm text-muted">Create tenants and inspect business accounts.</p>
      </div>
      {error && <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <form
        onSubmit={handleCreate}
        className="mt-6 grid gap-3 rounded-md border border-line bg-panel p-4 md:grid-cols-5"
      >
        <input
          className="rounded-md border border-line px-3 py-2"
          placeholder="Tenant name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />
        <input
          className="rounded-md border border-line px-3 py-2"
          placeholder="tenant-slug"
          value={slug}
          onChange={(event) => setSlug(event.target.value)}
          required
        />
        <input
          className="rounded-md border border-line px-3 py-2"
          placeholder="owner@example.com"
          value={ownerEmail}
          onChange={(event) => setOwnerEmail(event.target.value)}
        />
        <input
          className="rounded-md border border-line px-3 py-2"
          placeholder="Owner password"
          type="password"
          value={ownerPassword}
          onChange={(event) => setOwnerPassword(event.target.value)}
          minLength={8}
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-ink px-3 py-2 font-semibold text-white disabled:opacity-60"
        >
          {loading ? "Creating" : "Create tenant"}
        </button>
      </form>
      <section className="mt-6 rounded-md border border-line bg-panel">
        <div className="grid gap-2 border-b border-line px-4 py-3 text-sm font-semibold text-muted md:grid-cols-5">
          <div>Name</div>
          <div>Slug</div>
          <div>Status</div>
          <div>Activity</div>
          <div>Action</div>
        </div>
        <div className="divide-y divide-line">
          {tenants.map((tenant) => (
            <div key={tenant.id} className="grid gap-2 px-4 py-3 text-sm md:grid-cols-5">
              <div className="font-medium text-ink">{tenant.name}</div>
              <div className="text-muted">{tenant.slug}</div>
              <StatusPill value={tenant.status} />
              <div className="text-muted">
                {tenant.metrics.leads_total} leads, {tenant.metrics.conversations_total} chats
              </div>
              <Link className="font-semibold text-accent" href={`/admin/tenants/${tenant.id}`}>
                Open
              </Link>
            </div>
          ))}
          {tenants.length === 0 && (
            <div className="px-4 py-6 text-sm text-muted">No tenants available.</div>
          )}
        </div>
      </section>
    </AdminShell>
  );
}
