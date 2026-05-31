"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { adminApi } from "../../../lib/api/client";
import { storeAdminSession } from "../../../lib/auth/admin-session";

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@example.test");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await adminApi.login(email, password, mfaCode || undefined);
      storeAdminSession(response.access_token, response.session);
      router.replace("/admin");
    } catch {
      setError("Admin sign in failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-canvas px-4 py-10 text-ink">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-lg border border-line bg-panel p-6 shadow-[0_18px_48px_rgba(16,24,40,0.12)]"
      >
        <div className="text-xs font-semibold uppercase text-muted">AI Magnet Admin</div>
        <h2 className="sr-only">Super admin</h2>
        <h1 className="mt-2 text-2xl font-semibold">Platform command center</h1>
        <p className="mt-2 text-sm text-muted">
          Sign in to inspect tenants, usage, worker health, billing, and audit trails.
        </p>
        <label className="mt-6 block text-sm font-medium text-muted" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          className="mt-2 w-full rounded-md border border-line bg-white px-3 py-2 shadow-sm"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <label className="mt-4 block text-sm font-medium text-muted" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          className="mt-2 w-full rounded-md border border-line bg-white px-3 py-2 shadow-sm"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          type="password"
          minLength={8}
          required
        />
        <label className="mt-4 block text-sm font-medium text-muted" htmlFor="mfa-code">
          MFA code
        </label>
        <input
          id="mfa-code"
          className="mt-2 w-full rounded-md border border-line bg-white px-3 py-2 shadow-sm"
          value={mfaCode}
          onChange={(event) => setMfaCode(event.target.value)}
          autoComplete="one-time-code"
          inputMode="numeric"
          placeholder="Required when enabled"
        />
        {error && <div className="mt-4 text-sm font-medium text-red-700">{error}</div>}
        <button
          type="submit"
          disabled={loading}
          className="mt-5 w-full rounded-md bg-accent px-3 py-2.5 font-semibold text-white shadow-[0_10px_22px_rgba(31,111,235,0.24)] disabled:opacity-60"
        >
          {loading ? "Signing in" : "Sign in"}
        </button>
      </form>
    </main>
  );
}
