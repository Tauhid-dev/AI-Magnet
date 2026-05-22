"use client";

import { useEffect, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type { PortalWidget } from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

export default function WidgetPage() {
  const [widget, setWidget] = useState<PortalWidget | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadWidget() {
    const token = getToken();
    if (!token) {
      return;
    }
    setWidget(await portalApi.widget(token));
  }

  useEffect(() => {
    loadWidget();
  }, []);

  async function createKey() {
    const token = getToken();
    if (!token) {
      return;
    }
    setLoading(true);
    try {
      setWidget(await portalApi.createWidgetKey(token));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Widget</h1>
        <p className="mt-1 text-sm text-muted">Install code and public key status.</p>
      </div>
      <section className="rounded-lg border border-line bg-panel p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-sm text-muted">Current status</div>
            <div className="mt-2"><StatusPill value={widget?.status || "not_configured"} /></div>
          </div>
          <button
            type="button"
            className="rounded-md bg-accent px-4 py-2 font-semibold text-white disabled:opacity-60"
            onClick={createKey}
            disabled={loading}
          >
            Create widget key
          </button>
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <div>
            <div className="text-sm font-semibold text-muted">Key prefix</div>
            <div className="mt-1 font-mono">{widget?.key_prefix || "-"}</div>
          </div>
          <div>
            <div className="text-sm font-semibold text-muted">New key</div>
            <div className="mt-1 break-all font-mono text-sm">{widget?.widget_key || "Shown only when a key is created."}</div>
          </div>
        </div>
        <div className="mt-5">
          <div className="text-sm font-semibold text-muted">Embed code</div>
          <pre className="mt-2 overflow-auto rounded-md bg-slate-950 p-4 text-sm text-slate-100">{widget?.embed_code || "Create a key to generate embed code."}</pre>
        </div>
      </section>
    </div>
  );
}
