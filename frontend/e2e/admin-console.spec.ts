import { expect, test } from "@playwright/test";
import { installMockApi } from "./support/mock-api";

test.beforeEach(async ({ page }) => {
  await installMockApi(page);
});

test("admin login exposes MFA UI and fails without a valid MFA code", async ({ page }) => {
  await page.goto("/admin/login");

  await expect(page.getByRole("heading", { name: "Super admin" })).toBeVisible();
  await expect(page.getByLabel("MFA code")).toHaveAttribute("placeholder", "Required when enabled");

  await page.getByLabel("Email").fill("admin@example.test");
  await page.getByLabel("Password").fill("admin-secure-pass");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByText("Admin sign in failed.")).toBeVisible();
  await expect(page).toHaveURL(/\/admin\/login$/);
});

test("admin login with MFA loads the synthetic admin console", async ({ page }) => {
  await page.goto("/admin/login");

  await page.getByLabel("Email").fill("admin@example.test");
  await page.getByLabel("Password").fill("admin-secure-pass");
  await page.getByLabel("MFA code").fill("123456");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page).toHaveURL(/\/admin$/);
  await expect(page.getByRole("heading", { name: "Platform overview" })).toBeVisible();
  await expect(page.getByText("super_admin")).toBeVisible();
  await expect(page.getByText("Demo Plumbing")).toBeVisible();

  await page.getByRole("link", { name: "Tenants" }).click();
  await expect(page.getByRole("heading", { name: "Tenants" })).toBeVisible();

  await page.getByPlaceholder("Tenant name").fill("E2E Repairs");
  await page.getByPlaceholder("tenant-slug").fill("e2e-repairs");
  await page.getByPlaceholder("owner@example.com").fill("owner-e2e@example.test");
  await page.getByPlaceholder("Owner password").fill("owner-secure-pass");
  await page.getByRole("button", { name: "Create tenant" }).click();

  await expect(page.getByText("E2E Repairs")).toBeVisible();
  await expect(page.getByText("e2e-repairs")).toBeVisible();
});
