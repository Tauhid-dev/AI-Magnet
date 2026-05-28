"use client";

import type { BusinessSession } from "../api/types";

const COOKIE_SESSION_TOKEN = "__cookie_session__";
const SESSION_KEY = "ai-magnet-business-session";

export function saveSession(_token: string, session: BusinessSession) {
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function getToken() {
  return window.localStorage.getItem(SESSION_KEY) ? COOKIE_SESSION_TOKEN : null;
}

export function getStoredSession(): BusinessSession | null {
  const raw = window.localStorage.getItem(SESSION_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as BusinessSession;
  } catch {
    return null;
  }
}

export function clearSession() {
  window.localStorage.removeItem(SESSION_KEY);
}
