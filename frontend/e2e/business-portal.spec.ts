import { expect, test } from "@playwright/test";
import { installMockApi } from "./support/mock-api";

test.beforeEach(async ({ page }) => {
  await installMockApi(page);
});

test("business login shows failure UI for invalid synthetic credentials", async ({ page }) => {
  await page.goto("/login");

  await page.getByLabel("Tenant slug").fill("demo-plumbing");
  await page.getByLabel("Email").fill("owner@example.test");
  await page.getByLabel("Password").fill("wrong-password");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page.getByText("Sign in failed for that tenant, email, and password.")).toBeVisible();
  await expect(page).toHaveURL(/\/login$/);
});

test("business login reaches the portal with synthetic API data", async ({ page }) => {
  await page.goto("/login");

  await page.getByLabel("Password").fill("correct-horse-battery");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page).toHaveURL(/\/portal$/);
  await expect(page.getByRole("heading", { name: "Overview" })).toBeVisible();
  await expect(page.getByText("Demo Plumbing").first()).toBeVisible();
  await expect(page.getByText("aim_live").first()).toBeVisible();
});

test("portal setup, knowledge, agent, lead, conversation, and widget screens render and update with mocks", async ({
  page
}) => {
  await signInAsBusiness(page);

  await page.getByRole("navigation").getByRole("link", { name: "Setup" }).click();
  await expect(page.getByRole("heading", { name: "Setup" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Launch checklist" })).toBeVisible();
  await expect(page.getByText("5/5")).toBeVisible();

  await page.getByLabel("Business name").fill("Demo Plumbing E2E");
  await page.getByLabel("Booking email").fill("bookings-e2e@demo-plumbing.example");
  await page.getByLabel("Website").fill("https://demo-plumbing.example/e2e");
  await page.getByRole("button", { name: "Save profile" }).click();
  await expect(page.getByText("Saved")).toBeVisible();

  await page.getByRole("navigation").getByRole("link", { name: "Knowledge" }).click();
  await expect(page.getByRole("heading", { name: "Knowledge" })).toBeVisible();
  await expect(page.getByText("demo-plumbing.example").first()).toBeVisible();
  await page.getByLabel("Website or sitemap URL").fill("https://new.demo-plumbing.example");
  await page.getByRole("button", { name: "Add source" }).click();
  await expect(page.getByRole("button", { name: "new.demo-plumbing.example" })).toBeVisible();

  await page.getByRole("navigation").getByRole("link", { name: "Agent test" }).click();
  await expect(page.getByRole("heading", { name: "Agent test" })).toBeVisible();
  await page.getByLabel("Visitor message").fill("Do you handle blocked drains in Bondi?");
  await page.getByRole("button", { name: "Run test" }).click();
  await expect(page.getByText("We can help with blocked drains in Bondi today.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Sources" })).toBeVisible();
  await expect(page.getByText("Service FAQ")).toBeVisible();

  await page.getByRole("navigation").getByRole("link", { name: "Leads" }).click();
  await expect(page.getByRole("heading", { name: "Leads" })).toBeVisible();
  await expect(page.getByText("Sam Visitor")).toBeVisible();
  await page.locator("select").selectOption("contacted");
  await expect(page.getByRole("row", { name: /Sam Visitor/ }).locator("td").nth(3)).toContainText("contacted");

  await page.getByRole("navigation").getByRole("link", { name: "Conversations" }).click();
  await expect(page.getByRole("heading", { name: "Conversations" })).toBeVisible();
  await page.getByRole("button", { name: /Sam Visitor/ }).click();
  await expect(page.getByText("Can you help with blocked drains today?")).toBeVisible();

  await page.getByRole("navigation").getByRole("link", { name: "Widget" }).click();
  await expect(page.getByRole("heading", { name: "Widget" })).toBeVisible();
  await expect(page.getByText("aim_live").first()).toBeVisible();
  await page.getByLabel("Widget title").fill("Ask Demo Plumbing E2E");
  await page.getByRole("button", { name: "Save title" }).click();
  await expect(page.getByLabel("Widget title")).toHaveValue("Ask Demo Plumbing E2E");
  await page
    .getByLabel("Allowed origins")
    .fill("https://demo-plumbing.example\nhttps://booking.demo-plumbing.example");
  await page.getByRole("button", { name: "Save origins" }).click();
  await expect(page.getByLabel("Allowed origins")).toHaveValue(
    "https://demo-plumbing.example\nhttps://booking.demo-plumbing.example"
  );
  await expect(page.getByText("data-widget-key=\"aim_live_synthetic_key\"")).toBeVisible();
});

async function signInAsBusiness(page: Parameters<typeof installMockApi>[0]) {
  await page.goto("/login");
  await page.getByLabel("Tenant slug").fill("demo-plumbing");
  await page.getByLabel("Email").fill("owner@example.test");
  await page.getByLabel("Password").fill("correct-horse-battery");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/portal$/);
}
