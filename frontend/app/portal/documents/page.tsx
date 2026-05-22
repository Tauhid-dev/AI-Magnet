"use client";

import { FormEvent, useEffect, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type { PortalDocument } from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<PortalDocument[]>([]);
  const [filename, setFilename] = useState("services.txt");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadDocuments() {
    const token = getToken();
    if (!token) {
      return;
    }
    setDocuments(await portalApi.documents(token));
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getToken();
    if (!token || !content.trim()) {
      return;
    }
    setLoading(true);
    try {
      await portalApi.uploadDocument(token, filename, content);
      setContent("");
      await loadDocuments();
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Knowledge</h1>
        <p className="mt-1 text-sm text-muted">Tenant documents and ingestion state.</p>
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
          <button className="rounded-md bg-accent px-4 py-2 font-semibold text-white disabled:opacity-60" disabled={loading}>
            Upload
          </button>
        </div>
      </form>
      <div className="overflow-hidden rounded-lg border border-line bg-panel">
        <table className="w-full border-collapse text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-muted">
            <tr>
              <th className="px-4 py-3">File</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {documents.map((document) => (
              <tr key={document.id}>
                <td className="px-4 py-3 font-medium">{document.filename}</td>
                <td className="px-4 py-3"><StatusPill value={document.status} /></td>
                <td className="px-4 py-3 text-muted">{new Date(document.updated_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
