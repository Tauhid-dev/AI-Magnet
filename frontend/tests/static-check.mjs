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
assert.match(apiClient, /Authorization/);
assert.doesNotMatch(apiClient, /AI_API_KEY/);

const portalShell = read("components/PortalShell.tsx");
assert.match(portalShell, /getToken/);
assert.match(portalShell, /tenant_name/);

const widgetPage = read("app/portal/widget/page.tsx");
assert.match(widgetPage, /createWidgetKey/);

const documentsPage = read("app/portal/documents/page.tsx");
assert.match(documentsPage, /uploadDocument/);
