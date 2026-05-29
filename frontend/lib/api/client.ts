import type {
  AdminAuditLog,
  AdminHealth,
  AdminLoginResponse,
  AdminSession,
  BillingPlan,
  AdminSupportContext,
  AdminTenantDeleteResponse,
  AdminTenantDetail,
  AdminTenantPrivacyExport,
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
  PortalWebsiteCrawlPage,
  PortalWebsiteSource,
  PortalLead,
  PortalWidget,
  TenantSubscription,
  WorkerHeartbeat
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const COOKIE_SESSION_TOKEN = "__cookie_session__";

type RequestOptions = {
  token?: string | null;
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json"
  };
  if (options.method && options.method !== "GET") {
    headers["X-AI-Magnet-CSRF"] = "1";
  }
  if (options.token && options.token !== COOKIE_SESSION_TOKEN) {
    headers.Authorization = `Bearer ${options.token}`;
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
    credentials: "include"
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

async function requestForm<T>(
  path: string,
  token: string | null,
  formData: FormData
): Promise<T> {
  const headers: Record<string, string> = {
    "X-AI-Magnet-CSRF": "1"
  };
  if (token && token !== COOKIE_SESSION_TOKEN) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: formData,
    cache: "no-store",
    credentials: "include"
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const portalApi = {
  login(tenantSlug: string, email: string, password: string) {
    return request<LoginResponse>("/business-portal/auth/login", {
      method: "POST",
      body: { tenant_slug: tenantSlug, email, password }
    });
  },
  logout(token?: string | null) {
    return request<void>("/business-portal/auth/logout", {
      token,
      method: "POST"
    });
  },
  session(token?: string | null) {
    return request<BusinessSession>("/business-portal/session", { token });
  },
  profile(token?: string | null) {
    return request<PortalBusinessProfile>("/business-portal/profile", { token });
  },
  updateProfile(
    token: string | null,
    payload: {
      business_name: string;
      business_email?: string | null;
      business_phone?: string | null;
      website_url?: string | null;
    }
  ) {
    return request<PortalBusinessProfile>("/business-portal/profile", {
      token,
      method: "PATCH",
      body: payload
    });
  },
  documents(token?: string | null) {
    return request<PortalDocument[]>("/business-portal/documents", { token });
  },
  jobs(token?: string | null) {
    return request<BackgroundJob[]>("/business-portal/jobs", { token });
  },
  job(token: string | null, jobId: string) {
    return request<BackgroundJob>(`/business-portal/jobs/${jobId}`, { token });
  },
  uploadDocument(token: string | null, filename: string, content: string) {
    return request<PortalDocument>("/business-portal/documents", {
      token,
      method: "POST",
      body: { filename, content, content_type: "text/plain" }
    });
  },
  uploadDocumentFile(token: string | null, file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return requestForm<PortalDocument>("/business-portal/documents/upload", token, formData);
  },
  refreshDocument(token: string | null, documentId: string) {
    return request<PortalDocument>(`/business-portal/documents/${documentId}/refresh`, {
      token,
      method: "POST"
    });
  },
  deleteDocument(token: string | null, documentId: string) {
    return request<void>(`/business-portal/documents/${documentId}`, {
      token,
      method: "DELETE"
    });
  },
  websiteSources(token?: string | null) {
    return request<PortalWebsiteSource[]>("/business-portal/website-sources", { token });
  },
  createWebsiteSource(
    token: string | null,
    payload: {
      source_type: "website" | "sitemap";
      url: string;
      max_pages?: number;
      max_depth?: number;
    }
  ) {
    return request<PortalWebsiteSource>("/business-portal/website-sources", {
      token,
      method: "POST",
      body: payload
    });
  },
  refreshWebsiteSource(token: string | null, sourceId: string) {
    return request<PortalWebsiteSource>(`/business-portal/website-sources/${sourceId}/refresh`, {
      token,
      method: "POST"
    });
  },
  deleteWebsiteSource(token: string | null, sourceId: string) {
    return request<void>(`/business-portal/website-sources/${sourceId}`, {
      token,
      method: "DELETE"
    });
  },
  websiteSourcePages(token: string | null, sourceId: string) {
    return request<PortalWebsiteCrawlPage[]>(
      `/business-portal/website-sources/${sourceId}/pages`,
      { token }
    );
  },
  leads(token?: string | null) {
    return request<PortalLead[]>("/business-portal/leads", { token });
  },
  updateLeadStatus(token: string | null, leadId: string, status: string) {
    return request<PortalLead>(`/business-portal/leads/${leadId}/status`, {
      token,
      method: "PATCH",
      body: { status }
    });
  },
  conversations(token?: string | null) {
    return request<PortalConversation[]>("/business-portal/conversations", { token });
  },
  conversation(token: string | null, conversationId: string) {
    return request<PortalConversationDetail>(
      `/business-portal/conversations/${conversationId}`,
      { token }
    );
  },
  testAgent(token: string | null, message: string) {
    return request<PortalAgentTestResponse>("/business-portal/agent/test", {
      token,
      method: "POST",
      body: { message }
    });
  },
  widget(token?: string | null) {
    return request<PortalWidget>("/business-portal/widget", { token });
  },
  createWidgetKey(token: string | null, allowedOrigins: string[]) {
    return request<PortalWidget>("/business-portal/widget/keys", {
      token,
      method: "POST",
      body: { allowed_origins: allowedOrigins }
    });
  },
  updateWidgetOrigins(token: string | null, widgetId: string, allowedOrigins: string[]) {
    return request<PortalWidget>(`/business-portal/widget/${widgetId}/origins`, {
      token,
      method: "PATCH",
      body: { allowed_origins: allowedOrigins }
    });
  },
  updateWidgetBranding(token: string | null, widgetId: string, widgetTitle: string) {
    return request<PortalWidget>(`/business-portal/widget/${widgetId}/branding`, {
      token,
      method: "PATCH",
      body: { widget_title: widgetTitle }
    });
  },
  rotateWidgetKey(token: string | null, widgetId: string, allowedOrigins?: string[]) {
    return request<PortalWidget>(`/business-portal/widget/${widgetId}/rotate`, {
      token,
      method: "POST",
      body: allowedOrigins ? { allowed_origins: allowedOrigins } : undefined
    });
  },
  disableWidgetKey(token: string | null, widgetId: string) {
    return request<PortalWidget>(`/business-portal/widget/${widgetId}/disable`, {
      token,
      method: "POST"
    });
  },
  revokeWidgetKey(token: string | null, widgetId: string) {
    return request<PortalWidget>(`/business-portal/widget/${widgetId}/revoke`, {
      token,
      method: "POST"
    });
  },
  analytics(token?: string | null) {
    return request<PortalAnalytics>("/business-portal/analytics", { token });
  },
  billing(token?: string | null) {
    return request<PortalBilling>("/business-portal/billing", { token });
  }
};

export const adminApi = {
  login(email: string, password: string, mfaCode?: string) {
    return request<AdminLoginResponse>("/admin/auth/login", {
      method: "POST",
      body: { email, password, mfa_code: mfaCode || undefined }
    });
  },
  logout(token?: string | null) {
    return request<void>("/admin/auth/logout", {
      token,
      method: "POST"
    });
  },
  session(token?: string | null) {
    return request<AdminSession>("/admin/session", { token });
  },
  tenants(token?: string | null) {
    return request<AdminTenantSummary[]>("/admin/tenants", { token });
  },
  createTenant(
    token: string | null,
    payload: {
      name: string;
      slug: string;
      business_email?: string;
      owner_email?: string;
      owner_password?: string;
    }
  ) {
    return request<AdminTenantDetail>("/admin/tenants", {
      token,
      method: "POST",
      body: payload
    });
  },
  tenant(token: string | null, tenantId: string) {
    return request<AdminTenantDetail>(`/admin/tenants/${tenantId}`, { token });
  },
  updateTenantStatus(token: string | null, tenantId: string, status: string) {
    return request<AdminTenantDetail>(`/admin/tenants/${tenantId}/status`, {
      token,
      method: "PATCH",
      body: { status }
    });
  },
  offboardTenant(token: string | null, tenantId: string, retentionDays?: number) {
    return request<AdminTenantDetail>(`/admin/tenants/${tenantId}/offboard`, {
      token,
      method: "POST",
      body: { retention_days: retentionDays }
    });
  },
  privacyExport(token: string | null, tenantId: string) {
    return request<AdminTenantPrivacyExport>(
      `/admin/tenants/${tenantId}/privacy-export`,
      { token }
    );
  },
  deleteTenantData(token: string | null, tenantId: string, confirmSlug: string) {
    return request<AdminTenantDeleteResponse>(`/admin/tenants/${tenantId}/delete-data`, {
      token,
      method: "POST",
      body: { confirm_slug: confirmSlug, confirm_delete: true }
    });
  },
  supportContext(token: string | null, tenantId: string) {
    return request<AdminSupportContext>(`/admin/tenants/${tenantId}/support-context`, {
      token
    });
  },
  billingPlans(token?: string | null) {
    return request<BillingPlan[]>("/admin/billing/plans", { token });
  },
  tenantSubscription(token: string | null, tenantId: string) {
    return request<TenantSubscription | null>(`/admin/tenants/${tenantId}/subscription`, {
      token
    });
  },
  updateTenantSubscription(
    token: string | null,
    tenantId: string,
    payload: {
      plan_code: string;
      status: string;
      billing_contact_email?: string | null;
      manual_reference?: string | null;
      notes?: string | null;
    }
  ) {
    return request<TenantSubscription>(`/admin/tenants/${tenantId}/subscription`, {
      token,
      method: "PUT",
      body: payload
    });
  },
  usage(token?: string | null) {
    return request<AdminUsageOverview>("/admin/usage", { token });
  },
  health(token?: string | null) {
    return request<AdminHealth>("/admin/health", { token });
  },
  jobs(token?: string | null) {
    return request<BackgroundJob[]>("/admin/jobs", { token });
  },
  workerHeartbeats(token?: string | null) {
    return request<WorkerHeartbeat[]>("/admin/worker-heartbeats", { token });
  },
  auditLogs(token?: string | null) {
    return request<AdminAuditLog[]>("/admin/audit-logs", { token });
  }
};
