import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AI_STORAGE_KEY, aiStatusLine, createAiKeyStore } from "./ai-key";

const KEY = "test-key-not-real-0000";

function newStore() {
  return createAiKeyStore(() => window.sessionStorage);
}

describe("AI key holder (M5-AC2)", () => {
  let setItem: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    window.sessionStorage.clear();
    window.localStorage.clear();
    setItem = vi.spyOn(Storage.prototype, "setItem");
  });

  afterEach(() => {
    // localStorage is never written: no setItem call had localStorage as its target.
    expect(setItem.mock.contexts.filter((target: unknown) => target === window.localStorage)).toEqual([]);
    expect(window.localStorage.length).toBe(0);
    expect(document.cookie).toBe("");
    setItem.mockRestore();
  });

  it("keeps the key in memory only by default", () => {
    const store = newStore();
    store.setKey(KEY, { remember: false });
    expect(store.getSnapshot().key).toBe(KEY);
    expect(store.getSnapshot().remember).toBe(false);
    expect(window.sessionStorage.getItem(AI_STORAGE_KEY)).toBeNull();
    expect(setItem).not.toHaveBeenCalled();
    // A fresh page load (a new store) has nothing.
    expect(newStore().getSnapshot().key).toBeNull();
  });

  it("writes sessionStorage only with remember: true, under one key", () => {
    const store = newStore();
    store.setKey(KEY, { remember: true });
    store.setModel("example/model-a");
    expect(Object.keys(window.sessionStorage)).toEqual([AI_STORAGE_KEY]);
    expect(JSON.parse(window.sessionStorage.getItem(AI_STORAGE_KEY)!)).toEqual({ key: KEY, model: "example/model-a" });
    const reloaded = newStore().getSnapshot();
    expect([reloaded.key, reloaded.model, reloaded.remember]).toEqual([KEY, "example/model-a", true]);
  });

  it("unticking remember removes the stored copy but keeps the key in memory", () => {
    const store = newStore();
    store.setKey(KEY, { remember: true });
    store.setRemember(false);
    expect(window.sessionStorage.getItem(AI_STORAGE_KEY)).toBeNull();
    expect(store.getSnapshot().key).toBe(KEY);
  });

  it("clear() empties memory and sessionStorage and resets the status", () => {
    const store = newStore();
    store.setKey(KEY, { remember: true });
    store.setModel("example/model-a");
    store.setConnected("group 3");
    store.clear();
    const state = store.getSnapshot();
    expect([state.key, state.model, state.remember, state.connectedLabel, state.lastError]).toEqual([null, null, false, null, null]);
    expect(window.sessionStorage.getItem(AI_STORAGE_KEY)).toBeNull();
    expect(newStore().getSnapshot().key).toBeNull();
    expect(aiStatusLine(state)).toBe("AI not configured");
  });

  it("ignores a damaged stored value", () => {
    window.sessionStorage.setItem(AI_STORAGE_KEY, "{not json");
    setItem.mockClear();
    expect(newStore().getSnapshot().key).toBeNull();
  });

  it("notifies subscribers and gives a stable snapshot between changes", () => {
    const store = newStore();
    const listener = vi.fn();
    const unsubscribe = store.subscribe(listener);
    const before = store.getSnapshot();
    expect(store.getSnapshot()).toBe(before);
    store.setKey(KEY, { remember: false });
    expect(listener).toHaveBeenCalledTimes(1);
    unsubscribe();
    store.setModel("x");
    expect(listener).toHaveBeenCalledTimes(1);
  });
});

describe("status line", () => {
  const base = { key: null, model: null, remember: false, connectedLabel: null, lastError: null };
  it("names each state in words", () => {
    expect(aiStatusLine(base)).toBe("AI not configured");
    expect(aiStatusLine({ ...base, key: KEY })).toBe("Key set (memory only)");
    expect(aiStatusLine({ ...base, key: KEY, remember: true })).toBe("Key set (this tab)");
    expect(aiStatusLine({ ...base, key: KEY, connectedLabel: "group 3" })).toBe("Connected · group 3");
    expect(aiStatusLine({ ...base, key: KEY, connectedLabel: "group 3", lastError: "Key rejected" })).toBe("Key rejected");
  });

  it("never contains the key", () => {
    for (const remember of [false, true]) expect(aiStatusLine({ ...base, key: KEY, remember })).not.toContain(KEY);
  });
});
