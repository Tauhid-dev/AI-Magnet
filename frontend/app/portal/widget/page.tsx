"use client";

import { useEffect, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type { PortalWidget } from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

export default function WidgetPage() {
  const [widget, setWidget] = useState<PortalWidget | null>(null);
  const [originsText, setOriginsText] = useState("");
  const [widgetTitle, setWidgetTitle] = useState("Ask our AI receptionist");
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  async function loadWidget() {
    const token = getToken();
    if (!token) {
      return;
    }
    const nextWidget = await portalApi.widget(token);
    setWidget(nextWidget);
    setOriginsText(nextWidget.allowed_origins.join("\n"));
    setWidgetTitle(nextWidget.widget_title || "Ask our AI receptionist");
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
    setError(null);
    try {
      const nextWidget = await portalApi.createWidgetKey(token, parseOrigins(originsText));
      setWidget(nextWidget);
      setOriginsText(nextWidget.allowed_origins.join("\n"));
      setWidgetTitle(nextWidget.widget_title || widgetTitle);
    } catch {
      setError("Could not create the widget key. Check allowed origins and try again.");
    } finally {
      setLoading(false);
    }
  }

  async function updateOrigins() {
    const token = getToken();
    if (!token || !widget?.id) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const nextWidget = await portalApi.updateWidgetOrigins(
        token,
        widget.id,
        parseOrigins(originsText)
      );
      setWidget(nextWidget);
      setOriginsText(nextWidget.allowed_origins.join("\n"));
    } catch {
      setError("Could not update allowed origins.");
    } finally {
      setLoading(false);
    }
  }

  async function updateBranding() {
    const token = getToken();
    if (!token || !widget?.id) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const nextWidget = await portalApi.updateWidgetBranding(token, widget.id, widgetTitle);
      setWidget(nextWidget);
      setWidgetTitle(nextWidget.widget_title || widgetTitle);
    } catch {
      setError("Could not update widget branding.");
    } finally {
      setLoading(false);
    }
  }

  async function copyEmbedCode() {
    if (!widget?.embed_code) {
      return;
    }
    try {
      await navigator.clipboard.writeText(widget.embed_code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Embed code could not be copied.");
    }
  }

  async function rotateKey() {
    const token = getToken();
    if (!token || !widget?.id) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const nextWidget = await portalApi.rotateWidgetKey(token, widget.id, parseOrigins(originsText));
      setWidget(nextWidget);
      setOriginsText(nextWidget.allowed_origins.join("\n"));
    } catch {
      setError("Could not rotate the widget key.");
    } finally {
      setLoading(false);
    }
  }

  async function disableKey() {
    const token = getToken();
    if (!token || !widget?.id) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const nextWidget = await portalApi.disableWidgetKey(token, widget.id);
      setWidget(nextWidget);
    } catch {
      setError("Could not disable the widget key.");
    } finally {
      setLoading(false);
    }
  }

  async function revokeKey() {
    const token = getToken();
    if (!token || !widget?.id) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const nextWidget = await portalApi.revokeWidgetKey(token, widget.id);
      setWidget(nextWidget);
    } catch {
      setError("Could not revoke the widget key.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Widget</h1>
        <p className="mt-1 text-sm text-muted">Install code, allowed domains and public key status.</p>
      </div>
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <section className="rounded-lg border border-line bg-panel p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-sm text-muted">Current status</div>
            <div className="mt-2"><StatusPill value={widget?.status || "not_configured"} /></div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded-md bg-accent px-4 py-2 font-semibold text-white disabled:opacity-60"
              onClick={createKey}
              disabled={loading}
            >
              Create key
            </button>
            <button
              type="button"
              className="rounded-md border border-line px-4 py-2 font-semibold text-ink disabled:opacity-60"
              onClick={rotateKey}
              disabled={loading || !widget?.id}
            >
              Rotate
            </button>
            <button
              type="button"
              className="rounded-md border border-line px-4 py-2 font-semibold text-ink disabled:opacity-60"
              onClick={disableKey}
              disabled={loading || !widget?.id || widget?.status !== "active"}
            >
              Disable
            </button>
            <button
              type="button"
              className="rounded-md border border-red-200 px-4 py-2 font-semibold text-red-700 disabled:opacity-60"
              onClick={revokeKey}
              disabled={loading || !widget?.id || widget?.status === "revoked"}
            >
              Revoke
            </button>
          </div>
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
          <label className="text-sm font-semibold text-muted" htmlFor="widget-title">
            Widget title
          </label>
          <div className="mt-2 grid gap-3 md:grid-cols-[1fr_auto]">
            <input
              id="widget-title"
              className="rounded-md border border-line px-3 py-2"
              value={widgetTitle}
              onChange={(event) => setWidgetTitle(event.target.value)}
              maxLength={120}
            />
            <button
              type="button"
              className="rounded-md border border-line px-4 py-2 font-semibold text-ink disabled:opacity-60"
              onClick={updateBranding}
              disabled={loading || !widget?.id || widget?.status === "revoked" || !widgetTitle.trim()}
            >
              Save title
            </button>
          </div>
        </div>
        <div className="mt-5">
          <label className="text-sm font-semibold text-muted" htmlFor="allowed-origins">
            Allowed origins
          </label>
          <textarea
            id="allowed-origins"
            className="mt-2 min-h-28 w-full rounded-md border border-line px-3 py-2 font-mono text-sm"
            value={originsText}
            onChange={(event) => setOriginsText(event.target.value)}
            placeholder="https://example.com"
          />
          <div className="mt-2 flex justify-end">
            <button
              type="button"
              className="rounded-md border border-line px-4 py-2 font-semibold text-ink disabled:opacity-60"
              onClick={updateOrigins}
              disabled={loading || !widget?.id || widget?.status === "revoked"}
            >
              Save origins
            </button>
          </div>
        </div>
        <div className="mt-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-sm font-semibold text-muted">Embed code</div>
            <button
              type="button"
              className="rounded-md border border-line px-3 py-2 text-sm font-semibold text-ink disabled:opacity-60"
              onClick={copyEmbedCode}
              disabled={!widget?.embed_code}
            >
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
          <pre className="mt-2 overflow-auto rounded-md bg-slate-950 p-4 text-sm text-slate-100">{widget?.embed_code || "Create a key to generate embed code."}</pre>
        </div>
      </section>
    </div>
  );
}

function parseOrigins(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((origin) => origin.trim())
    .filter(Boolean);
}
