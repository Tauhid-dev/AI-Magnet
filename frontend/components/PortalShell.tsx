"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { BusinessSession } from "../lib/api/types";
import { portalApi } from "../lib/api/client";
import { clearSession, getStoredSession, getToken } from "../lib/auth/session";

const navItems = [
  { href: "/portal", label: "Overview" },
  { href: "/portal/onboarding", label: "Setup" },
  { href: "/portal/documents", label: "Knowledge" },
  { href: "/portal/agent", label: "Agent test" },
  { href: "/portal/leads", label: "Leads" },
  { href: "/portal/conversations", label: "Conversations" },
  { href: "/portal/widget", label: "Widget" },
  { href: "/portal/analytics", label: "Analytics" },
  { href: "/portal/billing", label: "Billing" }
];

export function PortalShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [session, setSession] = useState<BusinessSession | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function hydrateSession() {
      const token = getToken();
      const storedSession = getStoredSession();
      if (storedSession) {
        setSession(storedSession);
        return;
      }
      try {
        const serverSession = await portalApi.session(token);
        if (!cancelled) {
          setSession(serverSession);
        }
      } catch {
        if (!cancelled) {
          clearSession();
          router.replace("/login");
        }
      }
    }

    hydrateSession();
    return () => {
      cancelled = true;
    };
  }, [router]);

  if (!session) {
    return <main className="min-h-screen bg-canvas" />;
  }

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-[#263b58] bg-[#101b2c] text-white lg:block">
        <div className="border-b border-[#263b58] px-5 py-6">
          <div className="text-xs font-semibold uppercase text-[#9bb2ce]">AI Magnet Portal</div>
          <div className="mt-2 text-xl font-semibold">{session.tenant_name}</div>
          <div className="mt-1 text-xs text-[#9bb2ce]">
            AI receptionist operations desk.
          </div>
        </div>
        <nav className="space-y-1 p-4">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-md px-3 py-2 text-sm font-semibold ${active ? "bg-accent text-white shadow-[0_8px_18px_rgba(31,111,235,0.24)]" : "text-[#c4d1e3] hover:bg-[#172842] hover:text-white"}`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-line bg-panel/90 px-4 py-3 shadow-[0_6px_22px_rgba(16,24,40,0.04)] backdrop-blur lg:px-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-xs font-semibold uppercase text-muted">Business portal</div>
              <div className="mt-1 text-base font-semibold">
                {session.email} · {session.tenant_slug}
              </div>
            </div>
            <button
              type="button"
              className="rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold text-ink shadow-sm hover:bg-slate-50"
              onClick={async () => {
                await portalApi.logout(getToken()).catch(() => undefined);
                clearSession();
                router.replace("/login");
              }}
            >
              Sign out
            </button>
          </div>
          <nav className="mt-3 flex gap-2 overflow-x-auto lg:hidden">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`whitespace-nowrap rounded-md px-3 py-2 text-sm font-semibold ${pathname === item.href ? "bg-accent text-white" : "bg-slate-100 text-ink"}`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto max-w-[1500px] px-4 py-6 lg:px-6">{children}</main>
      </div>
    </div>
  );
}
