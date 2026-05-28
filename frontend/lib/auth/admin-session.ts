"use client";

import type { AdminSession } from "../api/types";

const COOKIE_SESSION_TOKEN = "__cookie_session__";
const SESSION_KEY = "ai_magnet_admin_session";

export function storeAdminSession(_token: string, session: AdminSession) {
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function getAdminToken(): string | null {
  return window.localStorage.getItem(SESSION_KEY) ? COOKIE_SESSION_TOKEN : null;
}

export function getStoredAdminSession(): AdminSession | null {
  const raw = window.localStorage.getItem(SESSION_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as AdminSession;
  } catch {
    clearAdminSession();
    return null;
  }
}

export function clearAdminSession() {
  window.localStorage.removeItem(SESSION_KEY);
}
