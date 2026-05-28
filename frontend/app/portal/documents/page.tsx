"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type {
  PortalDocument,
  PortalWebsiteCrawlPage,
  PortalWebsiteSource
} from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

type SourceType = "website" | "sitemap";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<PortalDocument[]>([]);
  const [sources, setSources] = useState<PortalWebsiteSource[]>([]);
  const [pages, setPages] = useState<PortalWebsiteCrawlPage[]>([]);
  const [activeSourceId, setActiveSourceId] = useState<string | null>(null);
  const [filename, setFilename] = useState("services.txt");
  const [content, setContent] = useState("");
  const [sourceType, setSourceType] = useState<SourceType>("website");
  const [sourceUrl, setSourceUrl] = useState("");
  const [maxPages, setMaxPages] = useState(10);
  const [maxDepth, setMaxDepth] = useState(1);
  const [loading, setLoading] = useState(false);
  const [sourceLoading, setSourceLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadKnowledge = useCallback(async () => {
    const token = getToken();
    if (!token) {
      return;
    }
    const [documentRows, sourceRows] = await Promise.all([
      portalApi.documents(token),
      portalApi.websiteSources(token)
    ]);
    setDocuments(documentRows);
    setSources(sourceRows);
    setActiveSourceId((current) => current || sourceRows[0]?.id || null);
  }, []);

  const loadPages = useCallback(async (sourceId: string | null) => {
    const token = getToken();
    if (!token || !sourceId) {
      setPages([]);
      return;
    }
    setPages(await portalApi.websiteSourcePages(token, sourceId));
  }, []);

  useEffect(() => {
    loadKnowledge();
  }, [loadKnowledge]);

  useEffect(() => {
    loadPages(activeSourceId);
  }, [activeSourceId, loadPages]);

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getToken();
    if (!token || !content.trim()) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await portalApi.uploadDocument(token, filename, content);
      setContent("");
      await loadKnowledge();
    } catch {
      setError("Document upload could not be queued.");
    } finally {
      setLoading(false);
    }
  }

  async function submitSource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getToken();
    if (!token || !sourceUrl.trim()) {
      return;
    }
    setSourceLoading(true);
    setError(null);
    try {
      const created = await portalApi.createWebsiteSource(token, {
        source_type: sourceType,
        url: sourceUrl,
        max_pages: maxPages,
        max_depth: maxDepth
      });
      setSourceUrl("");
      setActiveSourceId(created.id);
      await loadKnowledge();
    } catch {
      setError("Website or sitemap ingestion could not be queued.");
    } finally {
      setSourceLoading(false);
    }
  }

  async function refreshSource(sourceId: string) {
    const token = getToken();
    if (!token) {
      return;
    }
    setSourceLoading(true);
    setError(null);
    try {
      await portalApi.refreshWebsiteSource(token, sourceId);
      await loadKnowledge();
      await loadPages(sourceId);
    } catch {
      setError("Source refresh could not be queued.");
    } finally {
      setSourceLoading(false);
    }
  }

  async function deleteSource(sourceId: string) {
    const token = getToken();
    if (!token) {
      return;
    }
    setSourceLoading(true);
    setError(null);
    try {
      await portalApi.deleteWebsiteSource(token, sourceId);
      if (activeSourceId === sourceId) {
        setActiveSourceId(null);
        setPages([]);
      }
      await loadKnowledge();
    } catch {
      setError("Source could not be deleted.");
    } finally {
      setSourceLoading(false);
    }
  }

  const activeSource = sources.find((source) => source.id === activeSourceId) || null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Knowledge</h1>
        <p className="mt-1 text-sm text-muted">Tenant documents, website sources, and ingestion state.</p>
      </div>

      {error ? (
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <form onSubmit={submitSource} className="rounded-lg border border-line bg-panel p-4">
        <div className="grid gap-3 lg:grid-cols-[140px_1fr_110px_110px_auto]">
          <select
            className="rounded-md border border-line px-3 py-2"
            value={sourceType}
            onChange={(event) => setSourceType(event.target.value as SourceType)}
            aria-label="Source type"
          >
            <option value="website">Website</option>
            <option value="sitemap">Sitemap</option>
          </select>
          <input
            className="rounded-md border border-line px-3 py-2"
            value={sourceUrl}
            onChange={(event) => setSourceUrl(event.target.value)}
            aria-label="Website or sitemap URL"
            placeholder="https://example.com"
          />
          <input
            className="rounded-md border border-line px-3 py-2"
            type="number"
            min={1}
            max={100}
            value={maxPages}
            onChange={(event) => setMaxPages(Number(event.target.value))}
            aria-label="Maximum pages"
          />
          <input
            className="rounded-md border border-line px-3 py-2"
            type="number"
            min={0}
            max={5}
            value={maxDepth}
            onChange={(event) => setMaxDepth(Number(event.target.value))}
            aria-label="Maximum crawl depth"
            disabled={sourceType === "sitemap"}
          />
          <button
            className="rounded-md bg-accent px-4 py-2 font-semibold text-white disabled:opacity-60"
            disabled={sourceLoading}
          >
            Add source
          </button>
        </div>
      </form>

      <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
        <div className="overflow-hidden rounded-lg border border-line bg-panel">
          <table className="w-full border-collapse text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-muted">
              <tr>
                <th className="px-4 py-3">Source</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Last crawled</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {sources.map((source) => (
                <tr key={source.id} className={source.id === activeSourceId ? "bg-blue-50/40" : ""}>
                  <td className="px-4 py-3">
                    <button
                      className="text-left font-medium text-accent"
                      type="button"
                      onClick={() => setActiveSourceId(source.id)}
                    >
                      {source.normalized_domain}
                    </button>
                    <div className="mt-1 max-w-xl truncate text-xs text-muted">{source.root_url}</div>
                  </td>
                  <td className="px-4 py-3"><StatusPill value={source.status} /></td>
                  <td className="px-4 py-3 text-muted">
                    {source.last_crawled_at ? new Date(source.last_crawled_at).toLocaleString() : "Not crawled"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <button
                        className="rounded-md border border-line px-3 py-1.5 text-xs font-semibold disabled:opacity-60"
                        type="button"
                        disabled={sourceLoading}
                        onClick={() => refreshSource(source.id)}
                      >
                        Refresh
                      </button>
                      <button
                        className="rounded-md border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-700 disabled:opacity-60"
                        type="button"
                        disabled={sourceLoading}
                        onClick={() => deleteSource(source.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {sources.length === 0 ? (
                <tr>
                  <td className="px-4 py-5 text-muted" colSpan={4}>
                    No website or sitemap sources have been added.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>

        <div className="overflow-hidden rounded-lg border border-line bg-panel">
          <div className="border-b border-line px-4 py-3">
            <h2 className="font-semibold">Crawl history</h2>
            <p className="mt-1 truncate text-xs text-muted">
              {activeSource ? activeSource.root_url : "Select a source"}
            </p>
          </div>
          <div className="divide-y divide-line">
            {pages.map((page) => (
              <div key={page.id} className="px-4 py-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <span className="truncate font-medium">{page.title || page.canonical_url}</span>
                  <StatusPill value={page.status} />
                </div>
                <div className="mt-1 truncate text-xs text-muted">{page.canonical_url}</div>
                {page.error_message ? (
                  <div className="mt-1 text-xs text-red-700">{page.error_message}</div>
                ) : null}
              </div>
            ))}
            {pages.length === 0 ? (
              <div className="px-4 py-5 text-sm text-muted">No crawl history for this source yet.</div>
            ) : null}
          </div>
        </div>
      </div>

      <form onSubmit={upload} className="rounded-lg border border-line bg-panel p-4">
        <div className="grid gap-3 md:grid-cols-[240px_1fr_auto]">
          <input
            className="rounded-md border border-line px-3 py-2"
            value={filename}
            onChange={(event) => setFilename(event.target.value)}
            aria-label="Filename"
          />
          <textarea
            className="min-h-20 rounded-md border border-line px-3 py-2"
            value={content}
            onChange={(event) => setContent(event.target.value)}
            aria-label="Document text"
            placeholder="Paste service area, pricing, hours, FAQs, or booking policy text"
          />
          <button
            className="rounded-md bg-accent px-4 py-2 font-semibold text-white disabled:opacity-60"
            disabled={loading}
          >
            Upload
          </button>
        </div>
      </form>

      <div className="overflow-hidden rounded-lg border border-line bg-panel">
        <table className="w-full border-collapse text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-muted">
            <tr>
              <th className="px-4 py-3">Document</th>
              <th className="px-4 py-3">Source</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {documents.map((document) => (
              <tr key={document.id}>
                <td className="px-4 py-3 font-medium">{document.source_title || document.filename}</td>
                <td className="px-4 py-3 text-muted">
                  <div>{document.source_type}</div>
                  {document.source_url ? <div className="mt-1 max-w-lg truncate text-xs">{document.source_url}</div> : null}
                </td>
                <td className="px-4 py-3"><StatusPill value={document.status} /></td>
                <td className="px-4 py-3 text-muted">{new Date(document.updated_at).toLocaleString()}</td>
              </tr>
            ))}
            {documents.length === 0 ? (
              <tr>
                <td className="px-4 py-5 text-muted" colSpan={4}>
                  No knowledge documents have been indexed.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
