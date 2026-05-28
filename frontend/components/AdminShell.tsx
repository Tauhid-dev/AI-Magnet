"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { AdminSession } from "../lib/api/types";
import { adminApi } from "../lib/api/client";
import {
  clearAdminSession,
  getAdminToken,
  getStoredAdminSession
} from "../lib/auth/admin-session";

const navItems = [
  { href: "/admin", label: "Overview" },
  { href: "/admin/tenants", label: "Tenants" },
  { href: "/admin/usage", label: "Usage" },
  { href: "/admin/health", label: "Health" },
  { href: "/admin/audit", label: "Audit" }
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [session, setSession] = useState<AdminSession | null>(null);

  useEffect(() => {
    const token = getAdminToken();
    const storedSession = getStoredAdminSession();
    if (!token || !storedSession) {
      router.replace("/admin/login");
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
          <div className="text-sm font-semibold uppercase tracking-wide text-muted">
            AI Tradie Admin
          </div>
          <div className="mt-1 text-lg font-semibold">Platform console</div>
        </div>
        <nav className="p-3">
          {navItems.map((item) => {
            const active =
              pathname === item.href ||
              (item.href !== "/admin" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-md px-3 py-2 text-sm font-medium ${active ? "bg-ink text-white" : "text-ink hover:bg-slate-100"}`}
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
              <div className="text-base font-semibold">{session.role}</div>
            </div>
            <button
              type="button"
              className="rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold text-ink"
              onClick={async () => {
                await adminApi.logout(getAdminToken()).catch(() => undefined);
                clearAdminSession();
                router.replace("/admin/login");
              }}
            >
              Sign out
            </button>
          </div>
          <nav className="mt-3 flex gap-2 overflow-x-auto lg:hidden">
            {navItems.map((item) => {
              const active =
                pathname === item.href ||
                (item.href !== "/admin" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium ${active ? "bg-ink text-white" : "bg-slate-100 text-ink"}`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
      </div>
    </div>
  );
}
