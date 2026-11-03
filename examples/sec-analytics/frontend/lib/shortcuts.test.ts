import { afterEach, describe, expect, it } from "vitest";

import { isFocusSearchShortcut } from "./shortcuts";

function setup() {
  document.body.innerHTML = `
    <input id="search" type="search" />
    <input id="other" type="text" />
    <textarea id="notes"></textarea>
    <div id="editor" contenteditable="true"><span id="inside">x</span></div>
    <button id="button">Go</button>`;
  const byId = (id: string) => document.getElementById(id) as HTMLElement;
  return { search: byId("search"), other: byId("other"), notes: byId("notes"), inside: byId("inside"), button: byId("button") };
}

function key(init: KeyboardEventInit, target: EventTarget | null) {
  const event = new KeyboardEvent("keydown", { bubbles: true, cancelable: true, ...init });
  Object.defineProperty(event, "target", { value: target });
  return event;
}

afterEach(() => {
  document.body.innerHTML = "";
});

describe("isFocusSearchShortcut", () => {
  it("'/' focuses search from the page or a button", () => {
    const { search, button } = setup();
    expect(isFocusSearchShortcut(key({ key: "/" }, document.body), search)).toBe(true);
    expect(isFocusSearchShortcut(key({ key: "/" }, button), search)).toBe(true);
  });

  it("Ctrl-K and Cmd-K focus search, in lower or upper case", () => {
    const { search } = setup();
    expect(isFocusSearchShortcut(key({ key: "k", ctrlKey: true }, document.body), search)).toBe(true);
    expect(isFocusSearchShortcut(key({ key: "k", metaKey: true }, document.body), search)).toBe(true);
    expect(isFocusSearchShortcut(key({ key: "K", ctrlKey: true }, document.body), search)).toBe(true);
  });

  it("ignores '/' while typing in any input, including the search box itself", () => {
    const { search, other, notes, inside } = setup();
    for (const target of [search, other, notes, inside]) {
      expect(isFocusSearchShortcut(key({ key: "/" }, target), search)).toBe(false);
    }
  });

  it("ignores Ctrl/Cmd-K while typing in another input", () => {
    const { search, other, notes, inside } = setup();
    for (const target of [other, notes, inside]) {
      expect(isFocusSearchShortcut(key({ key: "k", ctrlKey: true }, target), search)).toBe(false);
      expect(isFocusSearchShortcut(key({ key: "k", metaKey: true }, target), search)).toBe(false);
    }
  });

  it("keeps Ctrl/Cmd-K inside the search box itself (no browser search bar)", () => {
    const { search } = setup();
    expect(isFocusSearchShortcut(key({ key: "k", metaKey: true }, search), search)).toBe(true);
  });

  it("ignores other keys and other modifier combinations", () => {
    const { search } = setup();
    expect(isFocusSearchShortcut(key({ key: "k" }, document.body), search)).toBe(false);
    expect(isFocusSearchShortcut(key({ key: "/", ctrlKey: true }, document.body), search)).toBe(false);
    expect(isFocusSearchShortcut(key({ key: "/", altKey: true }, document.body), search)).toBe(false);
    expect(isFocusSearchShortcut(key({ key: "k", ctrlKey: true, shiftKey: true }, document.body), search)).toBe(false);
    expect(isFocusSearchShortcut(key({ key: "k", ctrlKey: true, altKey: true }, document.body), search)).toBe(false);
    expect(isFocusSearchShortcut(key({ key: "/", isComposing: true }, document.body), search)).toBe(false);
  });
});
