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
    <main className="flex min-h-screen items-center justify-center bg-canvas px-4 text-ink">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-md border border-line bg-panel p-5 shadow-sm"
      >
        <h1 className="text-xl font-semibold">Super admin</h1>
        <label className="mt-6 block text-sm font-medium text-muted" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          className="mt-2 w-full rounded-md border border-line px-3 py-2"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <label className="mt-4 block text-sm font-medium text-muted" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          className="mt-2 w-full rounded-md border border-line px-3 py-2"
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
          className="mt-2 w-full rounded-md border border-line px-3 py-2"
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
          className="mt-5 w-full rounded-md bg-ink px-3 py-2 font-semibold text-white disabled:opacity-60"
        >
          {loading ? "Signing in" : "Sign in"}
        </button>
      </form>
    </main>
  );
}
