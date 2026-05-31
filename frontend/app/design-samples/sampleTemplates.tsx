import Link from "next/link";

export type SampleId = "sample-1" | "sample-2" | "sample-3";
export type ScreenKey = "admin" | "portal" | "customer";

type Tone = "command" | "growth" | "governance";

export type Sample = {
  id: SampleId;
  number: string;
  name: string;
  stance: string;
  bestFor: string;
  tone: Tone;
  accent: string;
  accentSoft: string;
  dark: string;
  canvas: string;
  customerHeadline: string;
};

export const screenLabels: Record<ScreenKey, string> = {
  admin: "Admin page",
  portal: "Business portal",
  customer: "Customer page"
};

export const samples: Sample[] = [
  {
    id: "sample-1",
    number: "Sample 1",
    name: "Command Center",
    stance: "Dense, serious, operations-led console for a production AI platform.",
    bestFor: "Best when the redesign should feel like control software for admins and support operators.",
    tone: "command",
    accent: "#1f6feb",
    accentSoft: "#eef5ff",
    dark: "#101b2c",
    canvas: "#eef3f9",
    customerHeadline: "AI receptionist for urgent trade jobs"
  },
  {
    id: "sample-2",
    number: "Sample 2",
    name: "Growth Portal",
    stance: "Bright, guided, business-owner first design focused on leads and launch readiness.",
    bestFor: "Best when the product should feel approachable for customers while still premium.",
    tone: "growth",
    accent: "#008878",
    accentSoft: "#edf8f5",
    dark: "#102623",
    canvas: "#f4fbf9",
    customerHeadline: "Get a fast answer from Harbour Plumbing"
  },
  {
    id: "sample-3",
    number: "Sample 3",
    name: "Governance Studio",
    stance: "Trust, audit, quota, billing, and privacy controls as the center of the experience.",
    bestFor: "Best when production hardening and enterprise confidence matter most.",
    tone: "governance",
    accent: "#4169e1",
    accentSoft: "#eef2ff",
    dark: "#151923",
    canvas: "#f7f8fb",
    customerHeadline: "Verified AI support with source-backed answers"
  }
];

const adminMetrics = [
  ["Active tenants", "28", "+4 this week"],
  ["Conversations", "6,482", "82% handled"],
  ["Quota alerts", "3", "1 blocked"],
  ["Worker health", "99.2%", "4 queues live"]
];

const tenantRows = [
  ["Harbour Plumbing", "Business", "active", "82 chats", "$42.10"],
  ["Northern Spark", "Trial", "active", "34 chats", "$18.40"],
  ["Coastline HVAC", "Scale", "active", "116 chats", "$63.80"],
  ["Metro Locks", "Business", "paused", "7 chats", "$3.20"]
];

const leadRows = [
  ["Blocked drain", "Bondi", "urgent", "qualified"],
  ["Switchboard issue", "Manly", "today", "notified"],
  ["Leaking tap", "Parramatta", "week", "new"],
  ["Water heater", "Surry Hills", "today", "qualified"]
];

const auditRows = [
  ["tenant.status.updated", "Harbour Plumbing", "2 min ago"],
  ["widget.key.rotated", "Coastline HVAC", "19 min ago"],
  ["privacy.export.created", "Northern Spark", "1 hr ago"],
  ["billing.plan.changed", "Metro Locks", "2 hr ago"]
];

const knowledgeRows = [
  ["Website crawl", "128 pages", "complete"],
  ["Service guide", "34 chunks", "indexed"],
  ["Pricing notes", "12 chunks", "review"],
  ["Emergency FAQ", "18 chunks", "indexed"]
];

export function getSample(sampleId: string) {
  return samples.find((sample) => sample.id === sampleId);
}

export function isScreenKey(screen: string): screen is ScreenKey {
  return screen === "admin" || screen === "portal" || screen === "customer";
}

export function ScreenshotTemplate({ sample, screen }: { sample: Sample; screen: ScreenKey }) {
  if (screen === "admin") {
    return <AdminTemplate sample={sample} />;
  }
  if (screen === "portal") {
    return <PortalTemplate sample={sample} />;
  }
  return <CustomerTemplate sample={sample} />;
}

export function SampleLinks({ sample }: { sample: Sample }) {
  return (
    <div className="flex flex-wrap gap-2">
      {(Object.keys(screenLabels) as ScreenKey[]).map((screen) => (
        <Link
          className="rounded-md border border-[#cbd5e1] bg-white px-3 py-2 text-xs font-semibold text-[#344054]"
          href={`/design-samples/${sample.id}/${screen}`}
          key={screen}
        >
          {screenLabels[screen]}
        </Link>
      ))}
    </div>
  );
}

function AdminTemplate({ sample }: { sample: Sample }) {
  const darkAdmin = sample.tone === "governance";
  return (
    <TemplateShell sample={sample} screen="admin">
      <div className={`flex min-h-[860px] ${darkAdmin ? "bg-[#151923]" : "bg-white"}`}>
        <Sidebar sample={sample} active="Overview" dark={darkAdmin || sample.tone === "command"} />
        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar
            sample={sample}
            eyebrow="Platform admin"
            title={sample.tone === "governance" ? "Governance overview" : "Platform overview"}
            dark={darkAdmin}
          />
          <main className={`flex-1 p-6 ${darkAdmin ? "bg-[#1b202b]" : "bg-[#f6f8fb]"}`}>
            <div className="grid gap-4 lg:grid-cols-4">
              {adminMetrics.map(([label, value, detail]) => (
                <MetricTile dark={darkAdmin} detail={detail} key={label} label={label} sample={sample} value={value} />
              ))}
            </div>

            <div className="mt-5 grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
              <Panel dark={darkAdmin} title="Tenant operations" action="Open tenants">
                <div className="overflow-hidden rounded-md border border-[#dfe5ee]">
                  <div className={`grid grid-cols-[1.4fr_0.8fr_0.8fr_0.8fr_0.8fr] gap-3 px-4 py-3 text-xs font-semibold uppercase ${darkAdmin ? "border-[#303746] bg-[#252c39] text-[#aeb7c6]" : "bg-[#f1f4f8] text-[#667085]"}`}>
                    <span>Tenant</span>
                    <span>Plan</span>
                    <span>Status</span>
                    <span>Chats</span>
                    <span>Spend</span>
                  </div>
                  {tenantRows.map((row) => (
                    <div
                      className={`grid grid-cols-[1.4fr_0.8fr_0.8fr_0.8fr_0.8fr] gap-3 border-t px-4 py-3 text-sm ${darkAdmin ? "border-[#303746] text-[#e9edf5]" : "border-[#e6ebf2] text-[#243042]"}`}
                      key={`${sample.id}-${row[0]}`}
                    >
                      <strong>{row[0]}</strong>
                      <span>{row[1]}</span>
                      <Status value={row[2]} tone={row[2] === "active" ? "green" : "amber"} />
                      <span>{row[3]}</span>
                      <span>{row[4]}</span>
                    </div>
                  ))}
                </div>
              </Panel>

              <Panel dark={darkAdmin} title={sample.tone === "growth" ? "Tenant success queue" : "Risk and health"} action="Usage">
                <div className="space-y-4">
                  <Progress label="AI response quota" sample={sample} value="76%" />
                  <Progress label="Lead notifications" sample={sample} value="58%" />
                  <Progress label="Website crawl budget" sample={sample} value="42%" warning />
                  <Progress label="Audit coverage" sample={sample} value="91%" />
                </div>
                <div className="mt-5 grid gap-3 sm:grid-cols-2">
                  <MiniCard dark={darkAdmin} label="Failed jobs" value="2" />
                  <MiniCard dark={darkAdmin} label="Active workers" value="4" />
                </div>
              </Panel>
            </div>

            <div className="mt-5 grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
              <Panel dark={darkAdmin} title="Audit timeline" action="Audit">
                <div className="divide-y divide-[#e6ebf2]">
                  {auditRows.map(([event, tenant, time]) => (
                    <TimelineRow dark={darkAdmin} event={event} key={`${event}-${sample.id}`} tenant={tenant} time={time} />
                  ))}
                </div>
              </Panel>
              <Panel dark={darkAdmin} title="Billing and privacy controls" action="Billing">
                <div className="grid gap-4 md:grid-cols-[0.85fr_1.15fr]">
                  <BudgetRing sample={sample} />
                  <div className="grid gap-3 sm:grid-cols-2">
                    <MiniCard dark={darkAdmin} label="Current plan" value="Business" />
                    <MiniCard dark={darkAdmin} label="Privacy exports" value="14" />
                    <MiniCard dark={darkAdmin} label="Retention reviews" value="3" />
                    <MiniCard dark={darkAdmin} label="Support contexts" value="19" />
                  </div>
                </div>
              </Panel>
            </div>
          </main>
        </div>
      </div>
    </TemplateShell>
  );
}

function PortalTemplate({ sample }: { sample: Sample }) {
  const darkPortal = sample.tone === "command";
  return (
    <TemplateShell sample={sample} screen="portal">
      <div className={`flex min-h-[860px] ${darkPortal ? "bg-[#101b2c]" : "bg-white"}`}>
        <Sidebar sample={sample} active="Overview" dark={darkPortal} portal />
        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar
            sample={sample}
            eyebrow="Business portal"
            title={sample.tone === "growth" ? "Harbour Plumbing workspace" : "AI receptionist workspace"}
            dark={darkPortal}
          />
          <main className={`flex-1 p-6 ${darkPortal ? "bg-[#132139]" : "bg-[#f7fafc]"}`}>
            <div className="grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
              <Panel dark={darkPortal} title="Launch checklist" action="Setup">
                <div className="grid gap-4 md:grid-cols-[0.95fr_1.05fr]">
                  <Checklist sample={sample} dark={darkPortal} />
                  <div className="grid gap-3 sm:grid-cols-2">
                    <MetricTile dark={darkPortal} detail="+22% from chat" label="New leads" sample={sample} value="18" />
                    <MetricTile dark={darkPortal} detail="3 urgent" label="Booked jobs" sample={sample} value="7" />
                    <MetricTile dark={darkPortal} detail="2 need review" label="Open chats" sample={sample} value="9" />
                    <MetricTile dark={darkPortal} detail="128 pages crawled" label="Coverage" sample={sample} value="94%" />
                  </div>
                </div>
              </Panel>

              <Panel dark={darkPortal} title="Agent test" action="Run test">
                <div className={`rounded-md p-4 text-sm leading-6 ${darkPortal ? "bg-[#0f1b2c] text-[#d8e4f2]" : "bg-white text-[#344054]"}`}>
                  Visitor asks: Can you help with blocked drains in Bondi today?
                </div>
                <div className={`mt-3 rounded-md p-4 text-sm leading-6 ${darkPortal ? "bg-[#172b48] text-white" : "bg-[#eef5ff] text-[#153d75]"}`}>
                  Yes. We can help today, capture your address, and pass the job to the office with urgency marked.
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  <MiniCard dark={darkPortal} label="Sources" value="4" />
                  <MiniCard dark={darkPortal} label="Top score" value="0.842" />
                  <MiniCard dark={darkPortal} label="Safety" value="clear" />
                </div>
              </Panel>
            </div>

            <div className="mt-5 grid gap-5 xl:grid-cols-[0.92fr_1.08fr]">
              <Panel dark={darkPortal} title="Lead pipeline" action="Leads">
                <div className="space-y-3">
                  {leadRows.map(([job, suburb, urgency, status]) => (
                    <LeadRow dark={darkPortal} job={job} key={`${job}-${sample.id}`} status={status} suburb={suburb} urgency={urgency} />
                  ))}
                </div>
              </Panel>

              <Panel dark={darkPortal} title="Knowledge and website ingestion" action="Knowledge">
                <div className="grid gap-4 md:grid-cols-[1fr_0.85fr]">
                  <div className="space-y-3">
                    {knowledgeRows.map(([name, count, status]) => (
                      <KnowledgeRow count={count} dark={darkPortal} key={`${name}-${sample.id}`} name={name} status={status} />
                    ))}
                  </div>
                  <div>
                    <Progress label="Crawl completion" sample={sample} value="94%" />
                    <div className="mt-4 rounded-md border border-[#dfe5ee] p-4">
                      <div className={`text-xs font-semibold uppercase ${darkPortal ? "text-[#9bb2ce]" : "text-[#667085]"}`}>Widget status</div>
                      <div className={`mt-2 text-xl font-semibold ${darkPortal ? "text-white" : "text-[#101828]"}`}>Active</div>
                      <p className={`mt-2 text-xs leading-5 ${darkPortal ? "text-[#b8c8dc]" : "text-[#667085]"}`}>
                        Origins, title, embed code, and key rotation map to the existing widget API.
                      </p>
                    </div>
                  </div>
                </div>
              </Panel>
            </div>

            <Panel dark={darkPortal} title="Analytics snapshot" action="Analytics" className="mt-5">
              <div className="grid gap-4 lg:grid-cols-4">
                <MetricTile dark={darkPortal} detail="notified 54" label="Qualified leads" sample={sample} value="61" />
                <MetricTile dark={darkPortal} detail="412 answers" label="AI responses" sample={sample} value="412" />
                <MetricTile dark={darkPortal} detail="18 visitor messages" label="Conversations" sample={sample} value="39" />
                <MetricTile dark={darkPortal} detail="$42.10 used" label="Budget" sample={sample} value="51%" />
              </div>
            </Panel>
          </main>
        </div>
      </div>
    </TemplateShell>
  );
}

function CustomerTemplate({ sample }: { sample: Sample }) {
  const darkCustomer = sample.tone === "command";
  const governance = sample.tone === "governance";
  return (
    <TemplateShell sample={sample} screen="customer">
      <div className={`min-h-[860px] ${darkCustomer ? "bg-[#0f1b2c] text-white" : "bg-white text-[#101828]"}`}>
        <header className={`border-b px-10 py-5 ${darkCustomer ? "border-[#263b58]" : "border-[#e2e8f0]"}`}>
          <div className="flex items-center justify-between gap-6">
            <div>
              <div className="text-lg font-semibold">Harbour Plumbing</div>
              <div className={`text-xs ${darkCustomer ? "text-[#9bb2ce]" : "text-[#647084]"}`}>Service page with AI Magnet widget</div>
            </div>
            <nav className={`flex gap-5 text-sm font-semibold ${darkCustomer ? "text-[#c7d7ea]" : "text-[#344054]"}`}>
              <span>Services</span>
              <span>Pricing</span>
              <span>Emergency</span>
              <span>Contact</span>
            </nav>
          </div>
        </header>

        <main className="grid gap-8 px-10 py-10 xl:grid-cols-[1fr_420px]">
          <section>
            <div className={`rounded-lg border p-8 ${darkCustomer ? "border-[#263b58] bg-[#132139]" : "border-[#dfe5ee] bg-[#f8fafc]"}`}>
              <p className="text-xs font-semibold uppercase" style={{ color: sample.accent }}>
                Customer-facing page
              </p>
              <h1 className="mt-3 max-w-2xl text-5xl font-semibold leading-tight">{sample.customerHeadline}</h1>
              <p className={`mt-4 max-w-xl text-base leading-7 ${darkCustomer ? "text-[#c1d0e4]" : "text-[#586474]"}`}>
                The website can keep its own brand while the AI Magnet widget handles qualification,
                evidence-backed answers, lead capture, and notification routing.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <button className="rounded-md px-4 py-3 text-sm font-semibold text-white" style={{ backgroundColor: sample.accent }}>
                  Start chat
                </button>
                <button className={`rounded-md border px-4 py-3 text-sm font-semibold ${darkCustomer ? "border-[#3a5274]" : "border-[#cbd5e1]"}`}>
                  View services
                </button>
              </div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              {["Blocked drains", "Hot water", "Leak detection"].map((service) => (
                <div
                  className={`rounded-lg border p-5 ${darkCustomer ? "border-[#263b58] bg-[#132139]" : "border-[#dfe5ee] bg-white"}`}
                  key={`${service}-${sample.id}`}
                >
                  <div className="text-sm font-semibold">{service}</div>
                  <p className={`mt-2 text-xs leading-5 ${darkCustomer ? "text-[#9bb2ce]" : "text-[#667085]"}`}>
                    Pricing, service areas, and availability can be answered from tenant knowledge.
                  </p>
                </div>
              ))}
            </div>

            <div className={`mt-6 rounded-lg border p-5 ${darkCustomer ? "border-[#263b58] bg-[#132139]" : "border-[#dfe5ee] bg-white"}`}>
              <div className="text-sm font-semibold">Lead handoff preview</div>
              <div className="mt-4 grid gap-3 md:grid-cols-4">
                {["Name", "Phone", "Suburb", "Urgency"].map((field) => (
                  <div className={`rounded-md border px-3 py-3 text-sm ${darkCustomer ? "border-[#31496a] bg-[#0f1b2c] text-[#c1d0e4]" : "border-[#d7dee8] bg-[#f8fafc] text-[#667085]"}`} key={field}>
                    {field}
                  </div>
                ))}
              </div>
            </div>
          </section>

          <aside className={`rounded-lg border p-4 shadow-[0_18px_40px_rgba(15,23,42,0.14)] ${darkCustomer ? "border-[#31496a] bg-[#101b2c]" : "border-[#d9e0ea] bg-white"}`}>
            <div className="flex items-center justify-between border-b pb-4" style={{ borderColor: darkCustomer ? "#31496a" : "#e2e8f0" }}>
              <div>
                <div className="font-semibold">{governance ? "Verified AI support" : "Ask our AI receptionist"}</div>
                <div className={`text-xs ${darkCustomer ? "text-[#9bb2ce]" : "text-[#667085]"}`}>Usually replies in under a minute</div>
              </div>
              <Status value="online" tone="green" />
            </div>
            <div className="space-y-3 py-5">
              <ChatBubble dark={darkCustomer} mine={false}>Hi, can you help with a blocked drain in Bondi?</ChatBubble>
              <ChatBubble dark={darkCustomer} mine sample={sample}>
                Yes. We service Bondi today. Is the drain fully blocked or draining slowly?
              </ChatBubble>
              <ChatBubble dark={darkCustomer} mine={false}>Fully blocked, and it smells bad.</ChatBubble>
              <ChatBubble dark={darkCustomer} mine sample={sample}>
                I will mark that urgent. Can I grab your phone number for dispatch?
              </ChatBubble>
            </div>
            {governance ? (
              <div className={`rounded-md border p-3 text-xs leading-5 ${darkCustomer ? "border-[#31496a] bg-[#0f1b2c] text-[#b8c8dc]" : "border-[#dfe5ee] bg-[#f8fafc] text-[#667085]"}`}>
                Sources visible to admins: services.pdf, emergency-faq, website crawl. Privacy-safe lead capture only.
              </div>
            ) : null}
            <div className="mt-4 grid grid-cols-[1fr_auto] gap-2">
              <div className={`rounded-md border px-3 py-3 text-sm ${darkCustomer ? "border-[#31496a] bg-[#0f1b2c] text-[#9bb2ce]" : "border-[#d7dee8] bg-[#f8fafc] text-[#667085]"}`}>
                Type your message
              </div>
              <button className="rounded-md px-4 py-3 text-sm font-semibold text-white" style={{ backgroundColor: sample.accent }}>
                Send
              </button>
            </div>
          </aside>
        </main>
      </div>
    </TemplateShell>
  );
}

function TemplateShell({
  children,
  sample,
  screen
}: {
  children: React.ReactNode;
  sample: Sample;
  screen: ScreenKey;
}) {
  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: sample.canvas }}>
      <div className="mx-auto max-w-[1440px]">
        <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
          <div>
            <Link className="text-xs font-semibold uppercase text-[#526171]" href="/design-samples">
              Back to samples
            </Link>
            <h1 className="mt-2 text-3xl font-semibold text-[#101828]">
              {sample.number}: {sample.name} - {screenLabels[screen]}
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-[#596576]">{sample.stance}</p>
          </div>
          <SampleLinks sample={sample} />
        </div>
        <div className="overflow-hidden rounded-lg border border-[#cbd5e1] shadow-[0_18px_40px_rgba(15,23,42,0.14)]">
          {children}
        </div>
      </div>
    </div>
  );
}

function Sidebar({
  sample,
  active,
  dark,
  portal = false
}: {
  sample: Sample;
  active: string;
  dark: boolean;
  portal?: boolean;
}) {
  const items = portal
    ? ["Overview", "Setup", "Knowledge", "Agent test", "Leads", "Conversations", "Widget", "Analytics", "Billing"]
    : ["Overview", "Tenants", "Usage", "Billing", "Health", "Audit", "Privacy"];
  return (
    <aside className={`w-64 shrink-0 border-r p-4 ${dark ? "border-[#263b58] bg-[#101b2c] text-white" : "border-[#e2e8f0] bg-white text-[#172033]"}`}>
      <div className="px-2 py-3">
        <div className={`text-xs font-semibold uppercase ${dark ? "text-[#9bb2ce]" : "text-[#667085]"}`}>
          {portal ? "AI Magnet Portal" : "AI Magnet Admin"}
        </div>
        <div className="mt-1 text-lg font-semibold">{portal ? "Harbour Plumbing" : sample.name}</div>
      </div>
      <nav className="mt-4 space-y-1">
        {items.map((item) => (
          <div
            className={`rounded-md px-3 py-2 text-sm font-semibold ${
              item === active
                ? "text-white"
                : dark
                  ? "text-[#c4d1e3]"
                  : "text-[#4a5568]"
            }`}
            key={`${item}-${sample.id}`}
            style={{ backgroundColor: item === active ? sample.accent : "transparent" }}
          >
            {item}
          </div>
        ))}
      </nav>
    </aside>
  );
}

function Topbar({
  sample,
  eyebrow,
  title,
  dark
}: {
  sample: Sample;
  eyebrow: string;
  title: string;
  dark: boolean;
}) {
  return (
    <header className={`border-b px-6 py-4 ${dark ? "border-[#303746] bg-[#151923] text-white" : "border-[#e2e8f0] bg-white text-[#101828]"}`}>
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className={`text-xs font-semibold uppercase ${dark ? "text-[#aeb7c6]" : "text-[#667085]"}`}>{eyebrow}</div>
          <div className="mt-1 text-2xl font-semibold">{title}</div>
        </div>
        <div className="flex gap-2">
          <button className={`rounded-md border px-3 py-2 text-sm font-semibold ${dark ? "border-[#303746] text-[#d8deea]" : "border-[#cfd5e1] text-[#344054]"}`}>
            Last 7 days
          </button>
          <button className="rounded-md px-3 py-2 text-sm font-semibold text-white" style={{ backgroundColor: sample.accent }}>
            Export
          </button>
        </div>
      </div>
    </header>
  );
}

function Panel({
  title,
  action,
  children,
  dark,
  className = ""
}: {
  title: string;
  action: string;
  children: React.ReactNode;
  dark: boolean;
  className?: string;
}) {
  return (
    <section className={`rounded-lg border p-4 ${dark ? "border-[#303746] bg-[#1d2430] text-white" : "border-[#dfe5ee] bg-white text-[#101828]"} ${className}`}>
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold">{title}</h2>
        <span className={`text-xs font-semibold ${dark ? "text-[#8fb7ff]" : "text-[#1f6feb]"}`}>{action}</span>
      </div>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function MetricTile({
  label,
  value,
  detail,
  sample,
  dark
}: {
  label: string;
  value: string;
  detail: string;
  sample: Sample;
  dark: boolean;
}) {
  return (
    <div className={`rounded-lg border p-4 ${dark ? "border-[#303746] bg-[#1d2430] text-white" : "border-[#dfe5ee] bg-white text-[#101828]"}`}>
      <div className={`text-xs font-semibold uppercase ${dark ? "text-[#aeb7c6]" : "text-[#667085]"}`}>{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      <div className="mt-3 inline-flex rounded-md px-2 py-1 text-xs font-semibold" style={{ backgroundColor: sample.accentSoft, color: sample.accent }}>
        {detail}
      </div>
    </div>
  );
}

function Progress({
  label,
  value,
  sample,
  warning = false
}: {
  label: string;
  value: string;
  sample: Sample;
  warning?: boolean;
}) {
  return (
    <div>
      <div className="flex justify-between gap-3 text-xs font-semibold text-[#667085]">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-sm bg-[#e7edf4]">
        <div className="h-full rounded-sm" style={{ width: value, backgroundColor: warning ? "#d9902f" : sample.accent }} />
      </div>
    </div>
  );
}

function MiniCard({ label, value, dark }: { label: string; value: string; dark: boolean }) {
  return (
    <div className={`rounded-md border p-3 ${dark ? "border-[#303746] bg-[#151923]" : "border-[#e4e9f1] bg-[#f8fafc]"}`}>
      <div className="text-xs font-semibold uppercase text-[#667085]">{label}</div>
      <div className={`mt-1 text-lg font-semibold ${dark ? "text-white" : "text-[#101828]"}`}>{value}</div>
    </div>
  );
}

function Status({ value, tone }: { value: string; tone: "green" | "amber" | "red" | "blue" }) {
  const classes = {
    green: "border-[#bfe6d7] bg-[#ecfdf5] text-[#087443]",
    amber: "border-[#f6d79b] bg-[#fff8e8] text-[#996515]",
    red: "border-[#fac5c1] bg-[#fff1f0] text-[#b42318]",
    blue: "border-[#bdd7ff] bg-[#eef5ff] text-[#1f5fbf]"
  };
  return <span className={`inline-flex rounded-md border px-2 py-1 text-xs font-semibold ${classes[tone]}`}>{value}</span>;
}

function TimelineRow({
  event,
  tenant,
  time,
  dark
}: {
  event: string;
  tenant: string;
  time: string;
  dark: boolean;
}) {
  return (
    <div className={`grid grid-cols-[1fr_auto] gap-3 py-3 text-sm ${dark ? "text-[#e9edf5]" : "text-[#243042]"}`}>
      <div>
        <div className="font-semibold">{event}</div>
        <div className="mt-1 text-xs text-[#667085]">{tenant}</div>
      </div>
      <span className="text-xs font-semibold text-[#667085]">{time}</span>
    </div>
  );
}

function BudgetRing({ sample }: { sample: Sample }) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex h-28 w-28 items-center justify-center rounded-full border-[12px] bg-white" style={{ borderColor: sample.accent }}>
        <div className="text-center">
          <div className="text-2xl font-semibold text-[#101828]">83%</div>
          <div className="text-xs text-[#667085]">budget</div>
        </div>
      </div>
      <div>
        <div className="text-sm font-semibold">Monthly budget</div>
        <div className="mt-1 text-2xl font-semibold">$228k</div>
        <div className="mt-1 text-xs text-[#667085]">Forecast plus quota blockers</div>
      </div>
    </div>
  );
}

function Checklist({ sample, dark }: { sample: Sample; dark: boolean }) {
  return (
    <div className={`rounded-lg border p-4 ${dark ? "border-[#303746] bg-[#101b2c]" : "border-[#dfe5ee] bg-white"}`}>
      {["Business profile", "Website crawl", "Service areas", "Widget install", "Go-live review"].map((item, index) => (
        <div className="flex items-center gap-3 py-2 text-sm" key={`${sample.id}-${item}`}>
          <span className={`h-3 w-3 rounded-sm ${index < 4 ? "" : "border border-[#94a3b8]"}`} style={{ backgroundColor: index < 4 ? sample.accent : "transparent" }} />
          <span className={dark ? "text-[#d8e4f2]" : "text-[#344054]"}>{item}</span>
        </div>
      ))}
      <div className="mt-4">
        <Progress label="Ready to launch" sample={sample} value="80%" />
      </div>
    </div>
  );
}

function LeadRow({
  job,
  suburb,
  urgency,
  status,
  dark
}: {
  job: string;
  suburb: string;
  urgency: string;
  status: string;
  dark: boolean;
}) {
  return (
    <div className={`grid gap-3 rounded-md border px-3 py-3 text-sm sm:grid-cols-[1fr_auto_auto] sm:items-center ${dark ? "border-[#303746] bg-[#101b2c]" : "border-[#e4e9f1] bg-[#f8fafc]"}`}>
      <div>
        <div className={dark ? "font-semibold text-white" : "font-semibold text-[#101828]"}>{job}</div>
        <div className="mt-1 text-xs text-[#667085]">{suburb} - {urgency}</div>
      </div>
      <Status value={status} tone={status === "new" ? "blue" : "green"} />
      <span className="text-xs font-semibold text-[#1f6feb]">Review</span>
    </div>
  );
}

function KnowledgeRow({
  name,
  count,
  status,
  dark
}: {
  name: string;
  count: string;
  status: string;
  dark: boolean;
}) {
  return (
    <div className={`grid grid-cols-[1fr_auto_auto] gap-3 rounded-md border px-3 py-3 text-sm ${dark ? "border-[#303746] bg-[#101b2c] text-white" : "border-[#e4e9f1] bg-[#f8fafc] text-[#101828]"}`}>
      <strong>{name}</strong>
      <span className="text-[#667085]">{count}</span>
      <Status value={status} tone={status === "review" ? "amber" : "green"} />
    </div>
  );
}

function ChatBubble({
  children,
  mine = false,
  dark,
  sample
}: {
  children: React.ReactNode;
  mine?: boolean;
  dark: boolean;
  sample?: Sample;
}) {
  return (
    <div className={`flex ${mine ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[82%] rounded-md px-3 py-2 text-sm leading-5 ${
          mine
            ? "text-white"
            : dark
              ? "bg-[#1d2f49] text-[#d8e4f2]"
              : "bg-[#f1f5f9] text-[#344054]"
        }`}
        style={{ backgroundColor: mine ? sample?.accent : undefined }}
      >
        {children}
      </div>
    </div>
  );
}
