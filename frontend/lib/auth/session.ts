"use client";

import type { BusinessSession } from "../api/types";

const TOKEN_KEY = "ai-magnet-business-token";
const SESSION_KEY = "ai-magnet-business-session";

export function saveSession(token: string, session: BusinessSession) {
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function getToken() {
  return window.localStorage.getItem(TOKEN_KEY);
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
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(SESSION_KEY);
}
