"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { BusinessSession } from "../lib/api/types";
import { clearSession, getStoredSession, getToken } from "../lib/auth/session";

const navItems = [
  { href: "/portal", label: "Overview" },
  { href: "/portal/documents", label: "Knowledge" },
  { href: "/portal/leads", label: "Leads" },
  { href: "/portal/conversations", label: "Conversations" },
  { href: "/portal/widget", label: "Widget" },
  { href: "/portal/analytics", label: "Analytics" }
];

export function PortalShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [session, setSession] = useState<BusinessSession | null>(null);

  useEffect(() => {
    const token = getToken();
    const storedSession = getStoredSession();
    if (!token || !storedSession) {
      router.replace("/login");
      return;
    }
    setSession(storedSession);
  }, [router]);

  if (!session) {
    return <main className="min-h-screen bg-canvas" />;
  }

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-panel lg:block">
        <div className="border-b border-line px-5 py-5">
          <div className="text-sm font-semibold uppercase tracking-wide text-muted">AI Tradie</div>
          <div className="mt-1 text-lg font-semibold">{session.tenant_name}</div>
        </div>
        <nav className="p-3">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-md px-3 py-2 text-sm font-medium ${active ? "bg-accent text-white" : "text-ink hover:bg-slate-100"}`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-line bg-panel/95 px-4 py-3 backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-sm text-muted">{session.email}</div>
              <div className="text-base font-semibold">{session.tenant_slug}</div>
            </div>
            <button
              type="button"
              className="rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold text-ink"
              onClick={() => {
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
                className={`whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium ${pathname === item.href ? "bg-accent text-white" : "bg-slate-100 text-ink"}`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
      </div>
    </div>
  );
}
