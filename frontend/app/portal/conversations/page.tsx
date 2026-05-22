"use client";

import { useEffect, useState } from "react";
import { StatusPill } from "../../../components/StatusPill";
import { portalApi } from "../../../lib/api/client";
import type { PortalConversation, PortalConversationDetail } from "../../../lib/api/types";
import { getToken } from "../../../lib/auth/session";

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<PortalConversation[]>([]);
  const [selected, setSelected] = useState<PortalConversationDetail | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      return;
    }
    portalApi.conversations(token).then(setConversations);
  }, []);

  async function selectConversation(conversationId: string) {
    const token = getToken();
    if (!token) {
      return;
    }
    setSelected(await portalApi.conversation(token, conversationId));
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <section className="rounded-lg border border-line bg-panel">
        <div className="border-b border-line p-4">
          <h1 className="text-2xl font-semibold">Conversations</h1>
          <p className="mt-1 text-sm text-muted">Widget chat history.</p>
        </div>
        <div className="divide-y divide-line">
          {conversations.map((conversation) => (
            <button
              type="button"
              key={conversation.id}
              className="block w-full px-4 py-3 text-left hover:bg-slate-50"
              onClick={() => selectConversation(conversation.id)}
            >
              <div className="flex items-center justify-between gap-3">
                <span className="font-medium">{conversation.visitor_label || "Website visitor"}</span>
                <StatusPill value={conversation.status} />
              </div>
              <div className="mt-1 text-sm text-muted">{conversation.message_count} messages</div>
            </button>
          ))}
          {conversations.length === 0 ? <div className="p-4 text-sm text-muted">No conversations yet.</div> : null}
        </div>
      </section>
      <section className="min-h-96 rounded-lg border border-line bg-panel p-4">
        {selected ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <h2 className="font-semibold">{selected.visitor_label || "Website visitor"}</h2>
              <StatusPill value={selected.status} />
            </div>
            {selected.messages.map((message) => (
              <div key={message.id} className="rounded-md border border-line bg-slate-50 p-3">
                <div className="text-xs font-semibold uppercase text-muted">{message.sender_type}</div>
                <div className="mt-1 text-sm">{message.content}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-muted">Select a conversation.</div>
        )}
      </section>
    </div>
  );
}
