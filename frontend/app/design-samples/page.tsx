import Image from "next/image";
import Link from "next/link";
import { SampleLinks, samples, screenLabels, type ScreenKey } from "./sampleTemplates";

const inspirationSources = [
  {
    label: "Zendesk AI agents",
    url: "https://support.zendesk.com/hc/en-us/articles/9748041653658-Using-the-dashboard-to-monitor-and-manage-AI-agents-AI-agents-Advanced-only"
  },
  {
    label: "Zendesk reporting",
    url: "https://support.zendesk.com/hc/en-us/articles/9510024609178-Analyzing-AI-agent-performance-with-the-reporting-dashboard"
  },
  {
    label: "Intercom Fin",
    url: "https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained"
  },
  {
    label: "Stripe Dashboard",
    url: "https://docs.stripe.com/dashboard/basics"
  },
  {
    label: "Retool admin dashboards",
    url: "https://retool.com/use-case/admin-dashboard"
  }
];

const backendPages = [
  "Admin: overview, tenants, usage, billing, health, audit",
  "Portal: onboarding, knowledge, agent test, leads, conversations, widget, analytics, billing",
  "Customer: embedded widget, public chat, lead capture, evidence-backed answers"
];

export default function DesignSamplesPage() {
  return (
    <main className="min-h-screen bg-[#f5f7fb] text-[#152033]">
      <section className="border-b border-[#d9e0ea] bg-white">
        <div className="mx-auto max-w-[1520px] px-5 py-8 lg:px-8">
          <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
            <div className="max-w-4xl">
              <p className="text-xs font-semibold uppercase text-[#526171]">
                AI Magnet page-template samples
              </p>
              <h1 className="mt-2 text-3xl font-semibold text-[#101828] md:text-4xl">
                Multi-page screenshots for each design direction.
              </h1>
              <p className="mt-3 text-sm leading-6 text-[#5b6575]">
                These are coded page templates, not device mockups. Each sample includes an admin
                page, a business portal page, and a customer-facing page so the chosen direction can
                become the frontend redesign blueprint.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-sm">
              {samples.map((sample) => (
                <a
                  className="rounded-md border border-[#ccd6e2] bg-white px-3 py-2 font-semibold"
                  href={`#${sample.id}`}
                  key={sample.id}
                >
                  {sample.number}
                </a>
              ))}
            </div>
          </div>

          <div className="mt-6 grid gap-3 text-xs text-[#5b6575] xl:grid-cols-[1fr_1fr_1.2fr]">
            <div className="rounded-lg border border-[#d9e0ea] bg-[#f8fafc] p-4">
              <div className="font-semibold text-[#1d2939]">Backend consistency checked</div>
              <p className="mt-2 leading-5">
                The templates map to the existing Next routes and FastAPI contracts:
                <span className="font-mono"> /admin/*</span>,
                <span className="font-mono"> /business-portal/*</span>, and the widget/chat APIs.
              </p>
            </div>
            <div className="rounded-lg border border-[#d9e0ea] bg-[#f8fafc] p-4">
              <div className="font-semibold text-[#1d2939]">Included page surfaces</div>
              <div className="mt-2 space-y-1.5">
                {backendPages.map((page) => (
                  <div key={page}>{page}</div>
                ))}
              </div>
            </div>
            <div className="rounded-lg border border-[#d9e0ea] bg-[#f8fafc] p-4">
              <div className="font-semibold text-[#1d2939]">Reference products reviewed</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {inspirationSources.map((source) => (
                  <a
                    className="rounded-md border border-[#ccd6e2] bg-white px-2.5 py-1.5 font-medium text-[#345174]"
                    href={source.url}
                    key={source.label}
                    rel="noreferrer"
                    target="_blank"
                  >
                    {source.label}
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-[1520px] px-5 py-10 lg:px-8">
        <div className="space-y-10">
          {samples.map((sample) => (
            <section
              className="rounded-lg border border-[#d9e0ea] bg-white p-5 shadow-[0_14px_36px_rgba(15,23,42,0.08)]"
              id={sample.id}
              key={sample.id}
            >
              <div className="grid gap-5 lg:grid-cols-[0.72fr_1.28fr] lg:items-end">
                <div>
                  <p className="text-xs font-semibold uppercase text-[#526171]">{sample.number}</p>
                  <h2 className="mt-2 text-3xl font-semibold text-[#101828]">{sample.name}</h2>
                  <p className="mt-3 text-sm leading-6 text-[#596576]">{sample.stance}</p>
                  <p className="mt-2 text-sm leading-6 text-[#596576]">{sample.bestFor}</p>
                  <div className="mt-5">
                    <SampleLinks sample={sample} />
                  </div>
                </div>
                <div className="grid gap-3 sm:grid-cols-3">
                  {(Object.keys(screenLabels) as ScreenKey[]).map((screen) => (
                    <Link
                      className="group rounded-lg border border-[#d9e0ea] bg-[#f8fafc] p-3 transition hover:border-[#9fb8dd]"
                      href={`/design-samples/${sample.id}/${screen}`}
                      key={`${sample.id}-${screen}`}
                    >
                      <Image
                        alt={`${sample.number} ${screenLabels[screen]} screenshot`}
                        className="aspect-[16/10] w-full rounded-md border border-[#d9e0ea] bg-white object-cover object-top"
                        height={900}
                        loading="eager"
                        sizes="(min-width: 1024px) 27vw, 100vw"
                        src={`/design-samples/screenshots/${sample.id}-${screen}.png`}
                        unoptimized
                        width={1440}
                      />
                      <div className="mt-3 flex items-center justify-between gap-2">
                        <span className="text-sm font-semibold text-[#101828]">
                          {screenLabels[screen]}
                        </span>
                        <span className="text-xs font-semibold text-[#1f6feb] group-hover:underline">
                          Open
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </section>
          ))}
        </div>
      </div>
    </main>
  );
}
