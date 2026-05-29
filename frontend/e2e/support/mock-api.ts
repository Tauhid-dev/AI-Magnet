import type { Page, Request, Route } from "@playwright/test";
import type {
  AdminHealth,
  AdminLoginResponse,
  AdminSession,
  AdminTenantSummary,
  AdminUsageOverview,
  BackgroundJob,
  BusinessSession,
  LoginResponse,
  PortalAgentTestResponse,
  PortalAnalytics,
  PortalBilling,
  PortalBusinessProfile,
  PortalConversation,
  PortalConversationDetail,
  PortalDocument,
  PortalLead,
  PortalWebsiteCrawlPage,
  PortalWebsiteSource,
  PortalWidget,
  QuotaStatus
} from "../../lib/api/types";

const API_BASE_URL = "http://127.0.0.1:8000";
const NOW = "2026-05-30T09:00:00.000Z";

type MockApiState = {
  businessSession: BusinessSession;
  adminSession: AdminSession;
  profile: PortalBusinessProfile;
  analytics: PortalAnalytics;
  documents: PortalDocument[];
  sources: PortalWebsiteSource[];
  pages: PortalWebsiteCrawlPage[];
  jobs: BackgroundJob[];
  widget: PortalWidget;
  leads: PortalLead[];
  conversations: PortalConversation[];
  conversationDetails: Record<string, PortalConversationDetail>;
  adminUsage: AdminUsageOverview;
  adminHealth: AdminHealth;
  tenants: AdminTenantSummary[];
  billing: PortalBilling;
};

export async function installMockApi(page: Page) {
  const state = createMockState();
  await page.route(`${API_BASE_URL}/**`, async (route) => {
    await handleApiRoute(route, state);
  });
  return state;
}

async function handleApiRoute(route: Route, state: MockApiState) {
  const request = route.request();
  const method = request.method();
  const url = new URL(request.url());
  const path = url.pathname;

  if (method === "OPTIONS") {
    await route.fulfill({ status: 204, headers: corsHeaders(request) });
    return;
  }

  try {
    if (path === "/business-portal/auth/login" && method === "POST") {
      const body = request.postDataJSON() as Record<string, string>;
      if (
        body.tenant_slug === "demo-plumbing" &&
        body.email === "owner@example.test" &&
        body.password === "correct-horse-battery"
      ) {
        const response: LoginResponse = {
          access_token: "synthetic-business-token",
          token_type: "bearer",
          session: state.businessSession
        };
        await json(route, request, response);
        return;
      }
      await json(route, request, { detail: "Invalid credentials" }, 401);
      return;
    }

    if (path === "/business-portal/auth/logout" && method === "POST") {
      await json(route, request, undefined, 204);
      return;
    }

    if (path === "/business-portal/session" && method === "GET") {
      await json(route, request, state.businessSession);
      return;
    }

    if (path === "/business-portal/profile" && method === "GET") {
      await json(route, request, state.profile);
      return;
    }

    if (path === "/business-portal/profile" && method === "PATCH") {
      const body = request.postDataJSON() as Partial<PortalBusinessProfile>;
      state.profile = {
        ...state.profile,
        business_name: body.business_name ?? state.profile.business_name,
        business_email: body.business_email ?? state.profile.business_email,
        business_phone: body.business_phone ?? state.profile.business_phone,
        website_url: body.website_url ?? state.profile.website_url,
        updated_at: NOW
      };
      await json(route, request, state.profile);
      return;
    }

    if (path === "/business-portal/analytics" && method === "GET") {
      await json(route, request, state.analytics);
      return;
    }

    if (path === "/business-portal/documents" && method === "GET") {
      await json(route, request, state.documents);
      return;
    }

    if (path === "/business-portal/documents" && method === "POST") {
      const body = request.postDataJSON() as Record<string, string>;
      const document = createDocument(`doc-${state.documents.length + 1}`, body.filename);
      state.documents = [document, ...state.documents];
      state.analytics.documents_total = state.documents.length;
      await json(route, request, document);
      return;
    }

    if (path === "/business-portal/website-sources" && method === "GET") {
      await json(route, request, state.sources);
      return;
    }

    if (path === "/business-portal/website-sources" && method === "POST") {
      const body = request.postDataJSON() as Record<string, string | number>;
      const rootUrl = String(body.url);
      const source = createWebsiteSource(`src-${state.sources.length + 1}`, rootUrl);
      state.sources = [source, ...state.sources];
      state.jobs = [createJob(`job-${state.jobs.length + 1}`, "rag.website_crawl", "queued"), ...state.jobs];
      await json(route, request, source);
      return;
    }

    const sourcePagesMatch = path.match(/^\/business-portal\/website-sources\/([^/]+)\/pages$/);
    if (sourcePagesMatch && method === "GET") {
      await json(
        route,
        request,
        state.pages.filter((page) => page.source_id === sourcePagesMatch[1])
      );
      return;
    }

    if (path === "/business-portal/jobs" && method === "GET") {
      await json(route, request, state.jobs);
      return;
    }

    if (path === "/business-portal/agent/test" && method === "POST") {
      const response: PortalAgentTestResponse = {
        assistant_message:
          "We can help with blocked drains in Bondi today. Call the emergency line and mention the E2E booking note.",
        answer_status: "answered",
        retrieved_chunk_count: 1,
        retrieval_top_score: 0.932,
        rag_safety_flags: [],
        citations: [
          {
            citation_id: "1",
            document_id: "doc-1",
            chunk_id: "chunk-1",
            chunk_index: 0,
            score: 0.932,
            filename: "services.txt",
            source_type: "website",
            source_title: "Service FAQ",
            source_url: "https://demo-plumbing.example/services"
          }
        ]
      };
      state.analytics.recent_usage = [
        {
          event_type: "agent_sandbox_tested",
          event_source: "business_portal",
          attributes: { synthetic: true },
          created_at: NOW
        },
        ...state.analytics.recent_usage.filter((event) => event.event_type !== "agent_sandbox_tested")
      ];
      await json(route, request, response);
      return;
    }

    if (path === "/business-portal/widget" && method === "GET") {
      await json(route, request, state.widget);
      return;
    }

    if (path === "/business-portal/widget/keys" && method === "POST") {
      const body = request.postDataJSON() as { allowed_origins?: string[] };
      state.widget = widgetWithUpdates(state.widget, {
        id: "widget-1",
        status: "active",
        key_prefix: "aim_live",
        widget_key: "aim_live_synthetic_key",
        allowed_origins: body.allowed_origins ?? state.widget.allowed_origins
      });
      await json(route, request, state.widget);
      return;
    }

    const widgetActionMatch = path.match(/^\/business-portal\/widget\/([^/]+)\/([^/]+)$/);
    if (widgetActionMatch && method === "PATCH" && widgetActionMatch[2] === "origins") {
      const body = request.postDataJSON() as { allowed_origins?: string[] };
      state.widget = widgetWithUpdates(state.widget, {
        allowed_origins: body.allowed_origins ?? []
      });
      await json(route, request, state.widget);
      return;
    }

    if (widgetActionMatch && method === "PATCH" && widgetActionMatch[2] === "branding") {
      const body = request.postDataJSON() as { widget_title?: string };
      state.widget = widgetWithUpdates(state.widget, {
        widget_title: body.widget_title ?? state.widget.widget_title
      });
      await json(route, request, state.widget);
      return;
    }

    if (widgetActionMatch && method === "POST" && widgetActionMatch[2] === "rotate") {
      state.widget = widgetWithUpdates(state.widget, {
        key_prefix: "aim_rotated",
        widget_key: "aim_rotated_synthetic_key"
      });
      await json(route, request, state.widget);
      return;
    }

    if (widgetActionMatch && method === "POST" && widgetActionMatch[2] === "disable") {
      state.widget = widgetWithUpdates(state.widget, { status: "disabled" });
      await json(route, request, state.widget);
      return;
    }

    if (widgetActionMatch && method === "POST" && widgetActionMatch[2] === "revoke") {
      state.widget = widgetWithUpdates(state.widget, {
        status: "revoked",
        widget_key: null,
        embed_code: null
      });
      await json(route, request, state.widget);
      return;
    }

    if (path === "/business-portal/leads" && method === "GET") {
      await json(route, request, state.leads);
      return;
    }

    const leadStatusMatch = path.match(/^\/business-portal\/leads\/([^/]+)\/status$/);
    if (leadStatusMatch && method === "PATCH") {
      const body = request.postDataJSON() as { status?: string };
      state.leads = state.leads.map((lead) =>
        lead.id === leadStatusMatch[1] ? { ...lead, status: body.status || lead.status } : lead
      );
      await json(route, request, state.leads.find((lead) => lead.id === leadStatusMatch[1]));
      return;
    }

    if (path === "/business-portal/conversations" && method === "GET") {
      await json(route, request, state.conversations);
      return;
    }

    const conversationMatch = path.match(/^\/business-portal\/conversations\/([^/]+)$/);
    if (conversationMatch && method === "GET") {
      await json(route, request, state.conversationDetails[conversationMatch[1]]);
      return;
    }

    if (path === "/business-portal/billing" && method === "GET") {
      await json(route, request, state.billing);
      return;
    }

    if (path === "/admin/auth/login" && method === "POST") {
      const body = request.postDataJSON() as Record<string, string>;
      if (
        body.email === "admin@example.test" &&
        body.password === "admin-secure-pass" &&
        body.mfa_code === "123456"
      ) {
        const response: AdminLoginResponse = {
          access_token: "synthetic-admin-token",
          token_type: "bearer",
          session: state.adminSession
        };
        await json(route, request, response);
        return;
      }
      await json(route, request, { detail: "Admin MFA required" }, 401);
      return;
    }

    if (path === "/admin/auth/logout" && method === "POST") {
      await json(route, request, undefined, 204);
      return;
    }

    if (path === "/admin/usage" && method === "GET") {
      await json(route, request, state.adminUsage);
      return;
    }

    if (path === "/admin/health" && method === "GET") {
      await json(route, request, state.adminHealth);
      return;
    }

    if (path === "/admin/tenants" && method === "GET") {
      await json(route, request, state.tenants);
      return;
    }

    if (path === "/admin/tenants" && method === "POST") {
      const body = request.postDataJSON() as Record<string, string>;
      const tenant = createTenant(`tenant-${state.tenants.length + 1}`, body.name, body.slug);
      state.tenants = [tenant, ...state.tenants];
      state.adminUsage.tenants_total = state.tenants.length;
      state.adminUsage.active_tenants = state.tenants.filter((item) => item.status === "active").length;
      await json(route, request, tenant);
      return;
    }

    await json(route, request, { detail: `Unhandled synthetic API route: ${method} ${path}` }, 500);
  } catch (error) {
    await json(route, request, { detail: error instanceof Error ? error.message : "Mock API failure" }, 500);
  }
}

function createMockState(): MockApiState {
  const quotaStatus: QuotaStatus = {
    period_start: "2026-05-01T00:00:00.000Z",
    period_end: "2026-06-01T00:00:00.000Z",
    warning_threshold_percent: 80,
    metrics: [
      {
        key: "ai_responses",
        label: "AI responses",
        used: 24,
        limit: 500,
        unit: "responses",
        percent_used: 4.8,
        warning: false,
        blocked: false
      }
    ],
    warnings: [],
    blocked_reasons: []
  };

  const businessSession: BusinessSession = {
    tenant_id: "tenant-1",
    tenant_name: "Demo Plumbing",
    tenant_slug: "demo-plumbing",
    user_id: "user-1",
    email: "owner@example.test",
    role: "owner"
  };

  const documents = [createDocument("doc-1", "services.txt")];
  const sources = [createWebsiteSource("src-1", "https://demo-plumbing.example")];
  const widget = widgetWithUpdates(
    {
      id: "widget-1",
      status: "active",
      key_prefix: "aim_live",
      widget_key: "aim_live_synthetic_key",
      embed_code: null,
      allowed_origins: ["https://demo-plumbing.example"],
      widget_title: "Ask Demo Plumbing"
    },
    {}
  );

  const analytics: PortalAnalytics = {
    documents_total: 1,
    documents_ingested: 1,
    documents_failed: 0,
    leads_total: 1,
    leads_qualified: 1,
    leads_notified: 1,
    conversations_total: 1,
    open_conversations: 1,
    messages_total: 2,
    visitor_messages_total: 1,
    assistant_messages_total: 1,
    usage_events_total: 3,
    ai_responses_total: 1,
    lead_notifications_sent: 1,
    widget_status: "active",
    lead_status_counts: [{ label: "qualified", count: 1 }],
    document_status_counts: [{ label: "ingested", count: 1 }],
    usage_event_counts: [
      { label: "agent_sandbox_tested", count: 1 },
      { label: "widget_key_created", count: 1 }
    ],
    recent_usage: [
      {
        event_type: "agent_sandbox_tested",
        event_source: "business_portal",
        attributes: { synthetic: true },
        created_at: NOW
      }
    ],
    quota_status: quotaStatus
  };

  const leads: PortalLead[] = [
    {
      id: "lead-1",
      conversation_id: "conversation-1",
      customer_name: "Sam Visitor",
      customer_email: "sam@example.test",
      customer_phone: "0400000000",
      job_type: "Blocked drain",
      suburb: "Bondi",
      urgency: "today",
      status: "qualified",
      qualified_at: NOW,
      qualification_reason: "Emergency plumbing request",
      notification_status: "sent",
      last_notified_at: NOW,
      notes: null,
      created_at: NOW
    }
  ];

  const conversations: PortalConversation[] = [
    {
      id: "conversation-1",
      visitor_label: "Sam Visitor",
      status: "open",
      source: "widget",
      created_at: NOW,
      message_count: 2
    }
  ];

  const tenants = [createTenant("tenant-1", "Demo Plumbing", "demo-plumbing")];

  return {
    businessSession,
    adminSession: {
      admin_id: "admin-1",
      email: "admin@example.test",
      full_name: "Synthetic Admin",
      role: "super_admin"
    },
    profile: {
      tenant_id: "tenant-1",
      tenant_name: "Demo Plumbing",
      tenant_slug: "demo-plumbing",
      tenant_status: "active",
      business_id: "business-1",
      business_name: "Demo Plumbing",
      business_email: "bookings@demo-plumbing.example",
      business_phone: "02 5550 0100",
      website_url: "https://demo-plumbing.example",
      updated_at: NOW
    },
    analytics,
    documents,
    sources,
    pages: [
      {
        id: "page-1",
        source_id: "src-1",
        url: "https://demo-plumbing.example/services",
        canonical_url: "https://demo-plumbing.example/services",
        title: "Services",
        status: "ingested",
        http_status: 200,
        error_message: null,
        document_id: "doc-1",
        crawled_at: NOW,
        created_at: NOW,
        updated_at: NOW
      }
    ],
    jobs: [createJob("job-1", "rag.website_crawl", "completed")],
    widget,
    leads,
    conversations,
    conversationDetails: {
      "conversation-1": {
        ...conversations[0],
        messages: [
          {
            id: "message-1",
            sender_type: "visitor",
            content: "Can you help with blocked drains today?",
            created_at: NOW
          },
          {
            id: "message-2",
            sender_type: "assistant",
            content: "Yes, we can help today and will collect your booking details.",
            created_at: NOW
          }
        ]
      }
    },
    adminUsage: {
      tenants_total: 1,
      active_tenants: 1,
      documents_total: 1,
      documents_ingested: 1,
      leads_total: 1,
      leads_qualified: 1,
      conversations_total: 1,
      messages_total: 2,
      usage_events_total: 3,
      ai_responses_total: 1,
      lead_notifications_sent: 1,
      admin_audit_events_total: 2,
      estimated_tokens_total: 1200,
      estimated_cost_cents_total: 42,
      pages_crawled_total: 3,
      storage_mb_total: 1.2,
      rate_limit_events_total: 0,
      quota_warning_tenants: 0,
      quota_blocked_tenants: 0,
      usage_event_counts: analytics.usage_event_counts,
      lead_status_counts: analytics.lead_status_counts,
      document_status_counts: analytics.document_status_counts,
      tenant_usage: [
        {
          tenant_id: "tenant-1",
          tenant_name: "Demo Plumbing",
          tenant_slug: "demo-plumbing",
          tenant_status: "active",
          documents_total: 1,
          leads_total: 1,
          conversations_total: 1,
          messages_total: 2,
          usage_events_total: 3,
          estimated_tokens: 1200,
          estimated_cost_cents: 42,
          quota_warnings: [],
          quota_blockers: []
        }
      ]
    },
    adminHealth: {
      status: "ready",
      database: "ok",
      queued_jobs: 0,
      running_jobs: 0,
      failed_jobs: 0,
      active_workers: 1,
      app_version: "e2e-synthetic",
      environment: "test"
    },
    tenants,
    billing: {
      subscription: {
        id: "subscription-1",
        tenant_id: "tenant-1",
        plan_code: "starter_beta",
        plan_name: "Starter Beta",
        status: "trialing",
        billing_mode: "manual",
        currency: "AUD",
        monthly_price_cents: 9900,
        support_level: "email",
        trial_ends_at: "2026-06-30T00:00:00.000Z",
        current_period_ends_at: "2026-06-30T00:00:00.000Z",
        canceled_at: null
      },
      available_plans: [],
      quota_status: quotaStatus,
      paid_beta_status: "manual_beta",
      payment_collection: "manual_invoice",
      privacy_operations: ["export", "offboard", "delete"],
      support_workflow: ["email_support"]
    }
  };
}

function createDocument(id: string, filename: string): PortalDocument {
  return {
    id,
    filename,
    content_type: "text/plain",
    status: "ingested",
    error_message: null,
    source_type: "uploaded_file",
    source_url: null,
    source_title: "Service FAQ",
    website_source_id: null,
    file_size_bytes: 2048,
    file_sha256: "synthetic-sha256",
    malware_scan_status: "clean",
    extraction_status: "completed",
    ocr_status: "not_required",
    job_id: null,
    created_at: NOW,
    updated_at: NOW
  };
}

function createWebsiteSource(id: string, rootUrl: string): PortalWebsiteSource {
  const parsed = new URL(rootUrl);
  return {
    id,
    source_type: "website",
    root_url: parsed.origin,
    normalized_domain: parsed.hostname,
    status: id === "src-1" ? "completed" : "queued",
    last_job_id: id === "src-1" ? "job-1" : null,
    last_error: null,
    max_pages: 10,
    max_depth: 1,
    last_crawled_at: id === "src-1" ? NOW : null,
    created_at: NOW,
    updated_at: NOW
  };
}

function createJob(id: string, jobType: string, status: string): BackgroundJob {
  return {
    id,
    tenant_id: "tenant-1",
    queue_name: "default",
    job_type: jobType,
    status,
    attempts: status === "queued" ? 0 : 1,
    max_attempts: 3,
    scheduled_at: NOW,
    started_at: status === "queued" ? null : NOW,
    completed_at: status === "completed" ? NOW : null,
    failed_at: null,
    locked_by: null,
    last_error: null,
    created_at: NOW,
    updated_at: NOW
  };
}

function createTenant(id: string, name: string, slug: string): AdminTenantSummary {
  return {
    id,
    name,
    slug,
    status: "active",
    offboarded_at: null,
    deletion_requested_at: null,
    data_retention_until: null,
    created_at: NOW,
    updated_at: NOW,
    metrics: {
      businesses_total: 1,
      users_total: 1,
      documents_total: id === "tenant-1" ? 1 : 0,
      leads_total: id === "tenant-1" ? 1 : 0,
      conversations_total: id === "tenant-1" ? 1 : 0,
      messages_total: id === "tenant-1" ? 2 : 0,
      usage_events_total: id === "tenant-1" ? 3 : 0
    }
  };
}

function widgetWithUpdates(widget: PortalWidget, updates: Partial<PortalWidget>): PortalWidget {
  const nextWidget = { ...widget, ...updates };
  return {
    ...nextWidget,
    embed_code:
      nextWidget.widget_key && nextWidget.status !== "revoked"
        ? `<script src="https://app.example.test/widget/chat-widget.js" data-widget-key="${nextWidget.widget_key}" data-title="${nextWidget.widget_title ?? "Ask us"}"></script>`
        : null
  };
}

async function json(
  route: Route,
  request: Request,
  body: unknown,
  status = 200
) {
  await route.fulfill({
    status,
    headers: {
      ...corsHeaders(request),
      "content-type": "application/json"
    },
    body: status === 204 ? "" : JSON.stringify(body)
  });
}

function corsHeaders(request: Request) {
  return {
    "access-control-allow-origin": request.headers().origin || "http://127.0.0.1:3100",
    "access-control-allow-credentials": "true",
    "access-control-allow-headers": "content-type, x-ai-magnet-csrf, authorization",
    "access-control-allow-methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS"
  };
}
