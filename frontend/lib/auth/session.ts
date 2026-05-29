"use client";

import type { BusinessSession } from "../api/types";

const COOKIE_SESSION_TOKEN = "__cookie_session__";
const SESSION_KEY = "ai-magnet-business-session";

export function saveSession(_token: string, session: BusinessSession) {
  getLocalStorage()?.setItem(SESSION_KEY, JSON.stringify(session));
}

export function getToken() {
  return COOKIE_SESSION_TOKEN;
}

export function getStoredSession(): BusinessSession | null {
  const raw = getLocalStorage()?.getItem(SESSION_KEY);
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
  getLocalStorage()?.removeItem(SESSION_KEY);
}

function getLocalStorage(): Storage | null {
  if (typeof window === "undefined" || !("localStorage" in window)) {
    return null;
  }
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}
