"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { portalApi } from "../../lib/api/client";
import { saveSession } from "../../lib/auth/session";

export default function LoginPage() {
  const router = useRouter();
  const [tenantSlug, setTenantSlug] = useState("demo-plumbing");
  const [email, setEmail] = useState("owner@example.test");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await portalApi.login(tenantSlug, email, password);
      saveSession(response.access_token, response.session);
      router.replace("/portal");
    } catch {
      setError("Sign in failed for that tenant, email, and password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-canvas px-4">
      <form onSubmit={onSubmit} className="w-full max-w-sm rounded-lg border border-line bg-panel p-5 shadow-sm">
        <h1 className="text-xl font-semibold text-ink">Business portal</h1>
        <div className="mt-5 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-muted">Tenant slug</span>
            <input
              className="mt-1 w-full rounded-md border border-line px-3 py-2"
              value={tenantSlug}
              onChange={(event) => setTenantSlug(event.target.value)}
              autoComplete="organization"
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-muted">Email</span>
            <input
              className="mt-1 w-full rounded-md border border-line px-3 py-2"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              type="email"
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-muted">Password</span>
            <input
              className="mt-1 w-full rounded-md border border-line px-3 py-2"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              type="password"
              minLength={8}
              required
            />
          </label>
        </div>
        {error ? <div className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}
        <button
          type="submit"
          className="mt-5 w-full rounded-md bg-accent px-4 py-2 font-semibold text-white disabled:opacity-60"
          disabled={loading}
        >
          {loading ? "Signing in" : "Sign in"}
        </button>
      </form>
    </main>
  );
}
