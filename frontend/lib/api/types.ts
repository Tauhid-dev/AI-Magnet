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
  qualified_at: string | null;
  qualification_reason: string | null;
  notification_status: string;
  last_notified_at: string | null;
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

export type AdminSession = {
  admin_id: string;
  email: string;
  full_name: string | null;
  role: string;
};

export type AdminLoginResponse = {
  access_token: string;
  token_type: "bearer";
  session: AdminSession;
};

export type AdminTenantMetrics = {
  businesses_total: number;
  users_total: number;
  documents_total: number;
  leads_total: number;
  conversations_total: number;
  messages_total: number;
  usage_events_total: number;
};

export type AdminTenantSummary = {
  id: string;
  name: string;
  slug: string;
  status: string;
  created_at: string;
  updated_at: string;
  metrics: AdminTenantMetrics;
};

export type AdminBusiness = {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  website_url: string | null;
  created_at: string;
};

export type AdminBusinessUser = {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  status: string;
  created_at: string;
};

export type AdminTenantDetail = AdminTenantSummary & {
  businesses: AdminBusiness[];
  users: AdminBusinessUser[];
};

export type AdminUsageOverview = {
  tenants_total: number;
  active_tenants: number;
  documents_total: number;
  leads_total: number;
  conversations_total: number;
  messages_total: number;
  usage_events_total: number;
};

export type AdminHealth = {
  status: string;
  database: string;
  app_version: string;
  environment: string;
};

export type AdminSupportContext = {
  tenant: AdminTenantSummary;
  recent_leads: Array<{
    id: string;
    status: string;
    job_type: string | null;
    suburb: string | null;
    urgency: string | null;
    has_contact: boolean;
    created_at: string;
  }>;
  recent_conversations: Array<{
    id: string;
    status: string;
    source: string;
    created_at: string;
    message_count: number;
  }>;
  recent_usage: Array<{
    event_type: string;
    event_source: string | null;
    attributes: Record<string, unknown>;
    created_at: string;
  }>;
};

export type AdminAuditLog = {
  id: string;
  tenant_id: string;
  actor_id: string | null;
  action: string;
  target_type: string | null;
  target_id: string | null;
  attributes: Record<string, unknown>;
  created_at: string;
};
