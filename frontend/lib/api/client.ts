import type {
  AdminAuditLog,
  AdminHealth,
  AdminLoginResponse,
  AdminSession,
  AdminSupportContext,
  AdminTenantDetail,
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

type RequestOptions = {
  token?: string;
  method?: "GET" | "POST" | "PATCH";
  body?: unknown;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json"
  };
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const portalApi = {
  login(tenantSlug: string, email: string) {
    return request<LoginResponse>("/business-portal/auth/login", {
      method: "POST",
      body: { tenant_slug: tenantSlug, email }
    });
  },
  session(token: string) {
    return request<BusinessSession>("/business-portal/session", { token });
  },
  documents(token: string) {
    return request<PortalDocument[]>("/business-portal/documents", { token });
  },
  uploadDocument(token: string, filename: string, content: string) {
    return request<PortalDocument>("/business-portal/documents", {
      token,
      method: "POST",
      body: { filename, content, content_type: "text/plain" }
    });
  },
  leads(token: string) {
    return request<PortalLead[]>("/business-portal/leads", { token });
  },
  updateLeadStatus(token: string, leadId: string, status: string) {
    return request<PortalLead>(`/business-portal/leads/${leadId}/status`, {
      token,
      method: "PATCH",
      body: { status }
    });
  },
  conversations(token: string) {
    return request<PortalConversation[]>("/business-portal/conversations", { token });
  },
  conversation(token: string, conversationId: string) {
    return request<PortalConversationDetail>(
      `/business-portal/conversations/${conversationId}`,
      { token }
    );
  },
  widget(token: string) {
    return request<PortalWidget>("/business-portal/widget", { token });
  },
  createWidgetKey(token: string) {
    return request<PortalWidget>("/business-portal/widget/keys", {
      token,
      method: "POST"
    });
  },
  analytics(token: string) {
    return request<PortalAnalytics>("/business-portal/analytics", { token });
  }
};

export const adminApi = {
  login(email: string) {
    return request<AdminLoginResponse>("/admin/auth/login", {
      method: "POST",
      body: { email }
    });
  },
  session(token: string) {
    return request<AdminSession>("/admin/session", { token });
  },
  tenants(token: string) {
    return request<AdminTenantSummary[]>("/admin/tenants", { token });
  },
  createTenant(
    token: string,
    payload: {
      name: string;
      slug: string;
      business_email?: string;
      owner_email?: string;
    }
  ) {
    return request<AdminTenantDetail>("/admin/tenants", {
      token,
      method: "POST",
      body: payload
    });
  },
  tenant(token: string, tenantId: string) {
    return request<AdminTenantDetail>(`/admin/tenants/${tenantId}`, { token });
  },
  updateTenantStatus(token: string, tenantId: string, status: string) {
    return request<AdminTenantDetail>(`/admin/tenants/${tenantId}/status`, {
      token,
      method: "PATCH",
      body: { status }
    });
  },
  supportContext(token: string, tenantId: string) {
    return request<AdminSupportContext>(`/admin/tenants/${tenantId}/support-context`, {
      token
    });
  },
  usage(token: string) {
    return request<AdminUsageOverview>("/admin/usage", { token });
  },
  health(token: string) {
    return request<AdminHealth>("/admin/health", { token });
  },
  auditLogs(token: string) {
    return request<AdminAuditLog[]>("/admin/audit-logs", { token });
  }
};
