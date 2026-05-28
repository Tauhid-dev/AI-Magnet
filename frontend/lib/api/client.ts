import type {
  AdminAuditLog,
  AdminHealth,
  AdminLoginResponse,
  AdminSession,
  AdminSupportContext,
  AdminTenantDeleteResponse,
  AdminTenantDetail,
  AdminTenantPrivacyExport,
  AdminTenantSummary,
  AdminUsageOverview,
  BusinessSession,
  LoginResponse,
  PortalAnalytics,
  PortalConversation,
  PortalConversationDetail,
  PortalDocument,
  PortalLead,
  PortalWidget
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const COOKIE_SESSION_TOKEN = "__cookie_session__";

type RequestOptions = {
  token?: string | null;
  method?: "GET" | "POST" | "PATCH";
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
  documents(token?: string | null) {
    return request<PortalDocument[]>("/business-portal/documents", { token });
  },
  uploadDocument(token: string | null, filename: string, content: string) {
    return request<PortalDocument>("/business-portal/documents", {
      token,
      method: "POST",
      body: { filename, content, content_type: "text/plain" }
    });
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
  usage(token?: string | null) {
    return request<AdminUsageOverview>("/admin/usage", { token });
  },
  health(token?: string | null) {
    return request<AdminHealth>("/admin/health", { token });
  },
  auditLogs(token?: string | null) {
    return request<AdminAuditLog[]>("/admin/audit-logs", { token });
  }
};
