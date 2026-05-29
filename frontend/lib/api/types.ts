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

export type PortalBusinessProfile = {
  tenant_id: string;
  tenant_name: string;
  tenant_slug: string;
  tenant_status: string;
  business_id: string | null;
  business_name: string | null;
  business_email: string | null;
  business_phone: string | null;
  website_url: string | null;
  updated_at: string | null;
};

export type PortalDocument = {
  id: string;
  filename: string;
  content_type: string | null;
  status: string;
  error_message: string | null;
  source_type: string;
  source_url: string | null;
  source_title: string | null;
  website_source_id: string | null;
  file_size_bytes: number | null;
  file_sha256: string | null;
  malware_scan_status: string;
  extraction_status: string;
  ocr_status: string;
  job_id: string | null;
  created_at: string;
  updated_at: string;
};

export type PortalWebsiteSource = {
  id: string;
  source_type: string;
  root_url: string;
  normalized_domain: string;
  status: string;
  last_job_id: string | null;
  last_error: string | null;
  max_pages: number;
  max_depth: number;
  last_crawled_at: string | null;
  created_at: string;
  updated_at: string;
};

export type PortalWebsiteCrawlPage = {
  id: string;
  source_id: string;
  url: string;
  canonical_url: string;
  title: string | null;
  status: string;
  http_status: number | null;
  error_message: string | null;
  document_id: string | null;
  crawled_at: string | null;
  created_at: string;
  updated_at: string;
};

export type BackgroundJob = {
  id: string;
  tenant_id?: string | null;
  queue_name?: string;
  job_type: string;
  status: string;
  attempts: number;
  max_attempts: number;
  scheduled_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  failed_at: string | null;
  locked_by?: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
};

export type WorkerHeartbeat = {
  worker_id: string;
  queue_name: string;
  status: string;
  hostname: string | null;
  pid: number | null;
  current_job_id: string | null;
  last_seen_at: string;
  stopping_at: string | null;
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
  allowed_origins: string[];
  widget_title: string | null;
};

export type PortalCitation = {
  citation_id: string;
  document_id: string;
  chunk_id: string;
  chunk_index: number;
  score: number;
  filename: string;
  source_type: string;
  source_title: string | null;
  source_url: string | null;
};

export type PortalAgentTestResponse = {
  assistant_message: string;
  answer_status: string;
  retrieved_chunk_count: number;
  citations: PortalCitation[];
  retrieval_top_score: number | null;
  rag_safety_flags: string[];
};

export type AnalyticsBreakdown = {
  label: string;
  count: number;
};

export type QuotaMetric = {
  key: string;
  label: string;
  used: number;
  limit: number;
  unit: string;
  percent_used: number;
  warning: boolean;
  blocked: boolean;
};

export type QuotaStatus = {
  period_start: string;
  period_end: string;
  warning_threshold_percent: number;
  metrics: QuotaMetric[];
  warnings: string[];
  blocked_reasons: string[];
};

export type PortalAnalytics = {
  documents_total: number;
  documents_ingested: number;
  documents_failed: number;
  leads_total: number;
  leads_qualified: number;
  leads_notified: number;
  conversations_total: number;
  open_conversations: number;
  messages_total: number;
  visitor_messages_total: number;
  assistant_messages_total: number;
  usage_events_total: number;
  ai_responses_total: number;
  lead_notifications_sent: number;
  widget_status: string;
  lead_status_counts: AnalyticsBreakdown[];
  document_status_counts: AnalyticsBreakdown[];
  usage_event_counts: AnalyticsBreakdown[];
  recent_usage: Array<{
    event_type: string;
    event_source: string | null;
    attributes: Record<string, unknown>;
    created_at: string;
  }>;
  quota_status: QuotaStatus;
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
  offboarded_at: string | null;
  deletion_requested_at: string | null;
  data_retention_until: string | null;
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
  documents_ingested: number;
  leads_total: number;
  leads_qualified: number;
  conversations_total: number;
  messages_total: number;
  usage_events_total: number;
  ai_responses_total: number;
  lead_notifications_sent: number;
  admin_audit_events_total: number;
  estimated_tokens_total: number;
  estimated_cost_cents_total: number;
  pages_crawled_total: number;
  storage_mb_total: number;
  rate_limit_events_total: number;
  quota_warning_tenants: number;
  quota_blocked_tenants: number;
  usage_event_counts: AnalyticsBreakdown[];
  lead_status_counts: AnalyticsBreakdown[];
  document_status_counts: AnalyticsBreakdown[];
  tenant_usage: Array<{
    tenant_id: string;
    tenant_name: string;
    tenant_slug: string;
    tenant_status: string;
    documents_total: number;
    leads_total: number;
    conversations_total: number;
    messages_total: number;
    usage_events_total: number;
    estimated_tokens: number;
    estimated_cost_cents: number;
    quota_warnings: string[];
    quota_blockers: string[];
  }>;
};

export type AdminHealth = {
  status: string;
  database: string;
  queued_jobs: number;
  running_jobs: number;
  failed_jobs: number;
  active_workers: number;
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
  scope: "tenant" | "global";
  tenant_id: string | null;
  actor_id: string | null;
  action: string;
  target_type: string | null;
  target_id: string | null;
  attributes: Record<string, unknown>;
  created_at: string;
};

export type AdminTenantPrivacyExport = {
  tenant_id: string;
  generated_at: string;
  data: Record<string, unknown>;
};

export type AdminTenantDeleteResponse = {
  tenant_id: string;
  tenant_slug: string;
  status: string;
  global_audit_id: string;
};
