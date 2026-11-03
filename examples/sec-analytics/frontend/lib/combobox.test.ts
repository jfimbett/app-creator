import { describe, expect, it } from "vitest";

import {
  CLOSED,
  type ComboboxState,
  activeDescendantId,
  comboboxKey,
  comboboxReducer,
  optionId,
} from "./combobox";

const withResults = (count: number): ComboboxState => comboboxReducer(CLOSED, { type: "results", count });

describe("comboboxReducer", () => {
  it("opens with no active item when results arrive", () => {
    expect(withResults(3)).toEqual({ open: true, activeIndex: -1, count: 3 });
  });

  it("stays open with zero results so the no-match message can show", () => {
    expect(withResults(0)).toEqual({ open: true, activeIndex: -1, count: 0 });
  });

  it("closes and forgets the active item", () => {
    const state = comboboxReducer(withResults(3), { type: "next" });
    expect(comboboxReducer(state, { type: "close" })).toEqual({ open: false, activeIndex: -1, count: 3 });
  });
});

describe("comboboxKey", () => {
  it("ArrowDown moves from no item to the first, then wraps from the last to the first", () => {
    let state = withResults(3);
    const steps: number[] = [];
    for (let i = 0; i < 4; i += 1) {
      state = comboboxKey(state, "ArrowDown").state;
      steps.push(state.activeIndex);
    }
    expect(steps).toEqual([0, 1, 2, 0]);
  });

  it("ArrowUp moves from no item to the last, then wraps from the first to the last", () => {
    let state = withResults(3);
    state = comboboxKey(state, "ArrowUp").state;
    expect(state.activeIndex).toBe(2);
    state = comboboxKey(comboboxKey(state, "ArrowUp").state, "ArrowUp").state;
    expect(state.activeIndex).toBe(0);
    expect(comboboxKey(state, "ArrowUp").state.activeIndex).toBe(2);
  });

  it("ArrowDown reopens a closed list that has results", () => {
    const closed = comboboxReducer(withResults(2), { type: "close" });
    const result = comboboxKey(closed, "ArrowDown");
    expect(result.state).toEqual({ open: true, activeIndex: 0, count: 2 });
    expect(result.handled).toBe(true);
  });

  it("arrows do nothing when there are no results", () => {
    const empty = withResults(0);
    expect(comboboxKey(empty, "ArrowDown")).toEqual({ state: empty, choose: null, handled: false });
    expect(comboboxKey(empty, "ArrowUp")).toEqual({ state: empty, choose: null, handled: false });
  });

  it("Enter chooses the active item and closes the list", () => {
    const state = comboboxKey(withResults(3), "ArrowDown").state;
    expect(comboboxKey(state, "Enter")).toEqual({
      state: { open: false, activeIndex: -1, count: 3 },
      choose: 0,
      handled: true,
    });
  });

  it("Enter with no active item does nothing", () => {
    const state = withResults(3);
    expect(comboboxKey(state, "Enter")).toEqual({ state, choose: null, handled: false });
  });

  it("Enter on a closed list does nothing, even if an index was remembered", () => {
    const closed: ComboboxState = { open: false, activeIndex: 1, count: 3 };
    expect(comboboxKey(closed, "Enter").choose).toBeNull();
  });

  it("Escape closes an open list", () => {
    const state = comboboxKey(withResults(3), "ArrowDown").state;
    expect(comboboxKey(state, "Escape")).toEqual({
      state: { open: false, activeIndex: -1, count: 3 },
      choose: null,
      handled: true,
    });
  });

  it("Escape on a closed list is not handled, and other keys are ignored", () => {
    expect(comboboxKey(CLOSED, "Escape").handled).toBe(false);
    const state = withResults(3);
    expect(comboboxKey(state, "a")).toEqual({ state, choose: null, handled: false });
  });
});

describe("ARIA ids", () => {
  it("builds option ids and the active descendant only while open with an active item", () => {
    expect(optionId("company-results", 2)).toBe("company-results-option-2");
    expect(activeDescendantId(withResults(3), "company-results")).toBeUndefined();
    const active = comboboxKey(withResults(3), "ArrowDown").state;
    expect(activeDescendantId(active, "company-results")).toBe("company-results-option-0");
    expect(activeDescendantId({ ...active, open: false }, "company-results")).toBeUndefined();
  });
});
