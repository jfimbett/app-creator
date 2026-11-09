"use client";

// The person's own OpenRouter key and model choice (M5, brief §3.1 and §7 "Key handling").
// By default they live only in this module's memory, so a reload forgets them. Only after the person ticks
// "Remember for this tab (sessionStorage)" are they copied to sessionStorage under one name, which the browser
// drops when the tab closes. Nothing here touches localStorage, cookies, IndexedDB or the URL, and this is not
// secure storage: any script on the page could read it.

import { useSyncExternalStore } from "react";

export const AI_STORAGE_KEY = "sec-analytics.ai";

export interface AiSettings {
  key: string | null;
  model: string | null;
  /** True when the key is also kept in sessionStorage for this tab. */
  remember: boolean;
  /** The key's label after a successful connection test. */
  connectedLabel: string | null;
  /** The message of the last AI error, shown as the status until the next success. */
  lastError: string | null;
  /** Counts key changes, so the model list can reload for a new key without using the key itself as a name. */
  keyVersion: number;
}

export const EMPTY_AI_SETTINGS: AiSettings = { key: null, model: null, remember: false, connectedLabel: null, lastError: null, keyVersion: 0 };

/** The status line in words (brief §3.1). It never contains the key. */
export function aiStatusLine(settings: Omit<AiSettings, "keyVersion">): string {
  if (!settings.key) return "AI not configured";
  if (settings.lastError) return settings.lastError;
  if (settings.connectedLabel !== null) return settings.connectedLabel ? `Connected · ${settings.connectedLabel}` : "Connected";
  return settings.remember ? "Key set (this tab)" : "Key set (memory only)";
}

function readStored(storage: Storage | null): Pick<AiSettings, "key" | "model"> | null {
  try {
    const raw = storage?.getItem(AI_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { key?: unknown; model?: unknown };
    if (typeof parsed.key !== "string" || !parsed.key) return null;
    return { key: parsed.key, model: typeof parsed.model === "string" && parsed.model ? parsed.model : null };
  } catch {
    return null;
  }
}

/** A store around a sessionStorage getter (the browser's by default; null on the server). */
export function createAiKeyStore(getStorage: () => Storage | null) {
  let state = EMPTY_AI_SETTINGS;
  let loaded = false;
  const listeners = new Set<() => void>();

  function storage(): Storage | null {
    try {
      return getStorage();
    } catch {
      return null; // storage blocked by the browser: memory only
    }
  }

  function load() {
    if (loaded) return;
    loaded = true;
    const stored = readStored(storage());
    if (stored) state = { ...EMPTY_AI_SETTINGS, ...stored, remember: true };
  }

  function persist() {
    const target = storage();
    if (!target) return;
    try {
      if (state.remember && state.key) target.setItem(AI_STORAGE_KEY, JSON.stringify({ key: state.key, model: state.model }));
      else target.removeItem(AI_STORAGE_KEY);
    } catch {
      // full or blocked storage: the key stays in memory only
    }
  }

  function update(next: Partial<AiSettings>) {
    load();
    const before = state;
    state = { ...state, ...next };
    if (before.remember || state.remember) persist();
    for (const listener of listeners) listener();
  }

  return {
    subscribe(listener: () => void) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
    getSnapshot(): AiSettings {
      load();
      return state;
    },
    /** A new key: the connection result and last error are reset; the model choice is kept. */
    setKey(key: string, { remember }: { remember: boolean }) {
      update({ key, remember, connectedLabel: null, lastError: null, keyVersion: state.keyVersion + 1 });
    },
    setModel(model: string | null) {
      update({ model });
    },
    setRemember(remember: boolean) {
      update({ remember });
    },
    setConnected(label: string | null) {
      update({ connectedLabel: label ?? "", lastError: null });
    },
    setError(message: string | null) {
      update({ lastError: message });
    },
    /** "Clear key": forgets the key and model in memory and in sessionStorage. */
    clear() {
      load();
      state = { ...EMPTY_AI_SETTINGS, keyVersion: state.keyVersion + 1 };
      try {
        storage()?.removeItem(AI_STORAGE_KEY);
      } catch {
        // nothing stored
      }
      for (const listener of listeners) listener();
    },
  };
}

export type AiKeyStore = ReturnType<typeof createAiKeyStore>;

/** The one store of this browser tab. */
export const aiKeyStore = createAiKeyStore(() => (typeof window === "undefined" ? null : window.sessionStorage));

const serverSnapshot = () => EMPTY_AI_SETTINGS;

/** The current key settings; components re-render when they change. */
export function useAiSettings(): AiSettings {
  return useSyncExternalStore(aiKeyStore.subscribe, aiKeyStore.getSnapshot, serverSnapshot);
}
