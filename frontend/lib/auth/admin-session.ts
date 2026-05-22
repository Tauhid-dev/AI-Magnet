"use client";

import type { AdminSession } from "../api/types";

const TOKEN_KEY = "ai_magnet_admin_token";
const SESSION_KEY = "ai_magnet_admin_session";

export function storeAdminSession(token: string, session: AdminSession) {
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function getAdminToken(): string | null {
  return window.localStorage.getItem(TOKEN_KEY);
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
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(SESSION_KEY);
}
