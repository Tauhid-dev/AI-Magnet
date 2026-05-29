import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = new URL("..", import.meta.url).pathname;

function read(path) {
  return readFileSync(join(root, path), "utf8");
}

const packageJson = JSON.parse(read("package.json"));
assert.equal(packageJson.dependencies.next.startsWith("^15."), true);
assert.equal(packageJson.devDependencies.tailwindcss.startsWith("^3."), true);

const apiClient = read("lib/api/client.ts");
assert.match(apiClient, /\/business-portal\/auth\/login/);
assert.match(apiClient, /\/admin\/auth\/login/);
assert.match(apiClient, /\/admin\/tenants/);
assert.match(apiClient, /\/admin\/usage/);
assert.match(apiClient, /Authorization/);
assert.doesNotMatch(apiClient, /AI_API_KEY/);

const portalShell = read("components/PortalShell.tsx");
assert.match(portalShell, /getToken/);
assert.match(portalShell, /tenant_name/);
assert.match(portalShell, /\/portal\/onboarding/);
assert.match(portalShell, /\/portal\/agent/);

const widgetPage = read("app/portal/widget/page.tsx");
assert.match(widgetPage, /createWidgetKey/);
assert.match(widgetPage, /updateWidgetBranding/);
assert.match(widgetPage, /navigator\.clipboard/);

const documentsPage = read("app/portal/documents/page.tsx");
assert.match(documentsPage, /uploadDocument/);
assert.match(documentsPage, /portalApi\.jobs/);

const onboardingPage = read("app/portal/onboarding/page.tsx");
assert.match(onboardingPage, /updateProfile/);
assert.match(onboardingPage, /Launch checklist/);
assert.match(onboardingPage, /agent_sandbox_tested/);

const agentTestPage = read("app/portal/agent/page.tsx");
assert.match(agentTestPage, /testAgent/);
assert.match(agentTestPage, /Sources/);

const adminShell = read("components/AdminShell.tsx");
assert.match(adminShell, /getAdminToken/);
assert.match(adminShell, /Platform console/);

const adminTenantsPage = read("app/admin/tenants/page.tsx");
assert.match(adminTenantsPage, /createTenant/);

const portalAnalyticsPage = read("app/portal/analytics/page.tsx");
assert.match(portalAnalyticsPage, /usage_event_counts/);

const adminUsagePage = read("app/admin/usage/page.tsx");
assert.match(adminUsagePage, /tenant_usage/);
