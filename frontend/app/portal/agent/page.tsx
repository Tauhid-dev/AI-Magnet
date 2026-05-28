"use client";

import { FormEvent, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type { PortalAgentTestResponse } from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

const DEFAULT_PROMPT = "Can you help with blocked drains in Bondi today?";

export default function AgentTestPage() {
  const [message, setMessage] = useState(DEFAULT_PROMPT);
  const [result, setResult] = useState<PortalAgentTestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submitTest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getToken();
    if (!token || !message.trim()) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setResult(await portalApi.testAgent(token, message));
    } catch {
      setError("Agent test could not be completed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
      <section className="rounded-lg border border-line bg-panel p-4">
        <div>
          <h1 className="text-2xl font-semibold">Agent test</h1>
          <p className="mt-1 text-sm text-muted">
            Sandbox answers use tenant knowledge and return source evidence.
          </p>
        </div>
        <form className="mt-5 space-y-4" onSubmit={submitTest}>
          <label className="block text-sm font-semibold text-muted" htmlFor="agent-message">
            Visitor message
          </label>
          <textarea
            id="agent-message"
            className="min-h-40 w-full rounded-md border border-line px-3 py-2 text-ink"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
          />
          {error ? (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          ) : null}
          <button
            className="rounded-md bg-accent px-4 py-2 font-semibold text-white disabled:opacity-60"
            disabled={loading || !message.trim()}
          >
            {loading ? "Testing..." : "Run test"}
          </button>
        </form>
      </section>

      <section className="min-h-96 rounded-lg border border-line bg-panel p-4">
        {result ? (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
              <div>
                <div className="text-sm font-semibold text-muted">Result</div>
                <div className="mt-2">
                  <StatusPill value={result.answer_status} />
                </div>
              </div>
              <div className="text-right text-sm text-muted">
                <div>{result.retrieved_chunk_count} retrieved chunks</div>
                <div>
                  Top score{" "}
                  {result.retrieval_top_score === null
                    ? "-"
                    : result.retrieval_top_score.toFixed(3)}
                </div>
              </div>
            </div>

            <div>
              <h2 className="font-semibold">Answer</h2>
              <div className="mt-2 whitespace-pre-wrap rounded-md bg-slate-50 p-4 text-sm leading-6">
                {result.assistant_message}
              </div>
            </div>

            {result.rag_safety_flags.length > 0 ? (
              <div>
                <h2 className="font-semibold">Safety flags</h2>
                <div className="mt-2 flex flex-wrap gap-2">
                  {result.rag_safety_flags.map((flag) => (
                    <span
                      className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800"
                      key={flag}
                    >
                      {flag}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}

            <div>
              <h2 className="font-semibold">Sources</h2>
              <div className="mt-2 space-y-3">
                {result.citations.map((citation) => (
                  <div className="rounded-md border border-line p-3 text-sm" key={citation.chunk_id}>
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="font-semibold">
                        [{citation.citation_id}] {citation.source_title || citation.filename}
                      </div>
                      <span className="text-xs font-semibold text-muted">
                        score {citation.score.toFixed(3)}
                      </span>
                    </div>
                    <div className="mt-1 text-xs text-muted">
                      {citation.source_type} · chunk {citation.chunk_index + 1}
                    </div>
                    {citation.source_url ? (
                      <a
                        className="mt-2 block truncate text-xs font-semibold text-accent"
                        href={citation.source_url}
                        rel="noreferrer"
                        target="_blank"
                      >
                        {citation.source_url}
                      </a>
                    ) : null}
                  </div>
                ))}
                {result.citations.length === 0 ? (
                  <div className="rounded-md bg-slate-50 p-4 text-sm text-muted">
                    No sources matched this message.
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex min-h-80 items-center justify-center rounded-md bg-slate-50 p-6 text-center text-sm text-muted">
            Run an agent test to see the answer, retrieval score, safety flags, and sources.
          </div>
        )}
      </section>
    </div>
  );
}
