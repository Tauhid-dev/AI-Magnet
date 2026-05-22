export type BusinessSession = {
  tenant_id: string;
  tenant_name: string;
  tenant_slug: string;
  user_id: string;
  email: string;
  role: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: "bearer";
  session: BusinessSession;
};

export type PortalDocument = {
  id: string;
  filename: string;
  content_type: string | null;
  status: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

export type PortalLead = {
  id: string;
  conversation_id: string | null;
  customer_name: string | null;
  customer_email: string | null;
  customer_phone: string | null;
  job_type: string | null;
  suburb: string | null;
  urgency: string | null;
  status: string;
  notes: string | null;
  created_at: string;
};

export type PortalConversation = {
  id: string;
  visitor_label: string | null;
  status: string;
  source: string;
  created_at: string;
  message_count: number;
};

export type PortalMessage = {
  id: string;
  sender_type: string;
  content: string;
  created_at: string;
};

export type PortalConversationDetail = PortalConversation & {
  messages: PortalMessage[];
};

export type PortalWidget = {
  id: string | null;
  status: string;
  key_prefix: string | null;
  widget_key: string | null;
  embed_code: string | null;
  allowed_origins: string | null;
};

export type PortalAnalytics = {
  documents_total: number;
  documents_ingested: number;
  leads_total: number;
  conversations_total: number;
  open_conversations: number;
  messages_total: number;
  widget_status: string;
  recent_usage: Array<{
    event_type: string;
    event_source: string | null;
    attributes: Record<string, unknown>;
    created_at: string;
  }>;
};
