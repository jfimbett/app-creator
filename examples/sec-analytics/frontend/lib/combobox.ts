// Pure keyboard logic for the company search combobox (WAI-ARIA combobox with a listbox popup).
// The component keeps this state and maps it to aria-expanded and aria-activedescendant.

/** `activeIndex` is -1 when no option is highlighted; `count` is the number of options shown. */
export interface ComboboxState {
  open: boolean;
  activeIndex: number;
  count: number;
}

export type ComboboxAction =
  | { type: "results"; count: number }
  | { type: "next" }
  | { type: "previous" }
  | { type: "close" };

/** Result of a key press: the new state, the option index to open (or null), and whether to preventDefault. */
export interface ComboboxKeyResult {
  state: ComboboxState;
  choose: number | null;
  handled: boolean;
}

export const CLOSED: ComboboxState = { open: false, activeIndex: -1, count: 0 };

/** State changes. New results open the list with nothing highlighted; ↑/↓ wrap around. */
export function comboboxReducer(state: ComboboxState, action: ComboboxAction): ComboboxState {
  switch (action.type) {
    case "results":
      return { open: true, activeIndex: -1, count: Math.max(0, action.count) };
    case "next":
      if (state.count === 0) return state;
      return { ...state, open: true, activeIndex: state.open ? (state.activeIndex + 1) % state.count : 0 };
    case "previous":
      if (state.count === 0) return state;
      return {
        ...state,
        open: true,
        activeIndex: state.open && state.activeIndex > 0 ? state.activeIndex - 1 : state.count - 1,
      };
    case "close":
      return { ...state, open: false, activeIndex: -1 };
  }
}

/** Handles ArrowDown, ArrowUp, Enter and Escape; other keys are left to the input. */
export function comboboxKey(state: ComboboxState, key: string): ComboboxKeyResult {
  const unchanged: ComboboxKeyResult = { state, choose: null, handled: false };
  switch (key) {
    case "ArrowDown":
    case "ArrowUp":
      if (state.count === 0) return unchanged;
      return { state: comboboxReducer(state, { type: key === "ArrowDown" ? "next" : "previous" }), choose: null, handled: true };
    case "Enter":
      if (!state.open || state.activeIndex < 0) return unchanged;
      return { state: comboboxReducer(state, { type: "close" }), choose: state.activeIndex, handled: true };
    case "Escape":
      if (!state.open) return unchanged;
      return { state: comboboxReducer(state, { type: "close" }), choose: null, handled: true };
    default:
      return unchanged;
  }
}

/** The id of option `index` inside the listbox `listboxId`. */
export function optionId(listboxId: string, index: number): string {
  return `${listboxId}-option-${index}`;
}

/** Value for aria-activedescendant: the highlighted option's id, or undefined. */
export function activeDescendantId(state: ComboboxState, listboxId: string): string | undefined {
  return state.open && state.activeIndex >= 0 ? optionId(listboxId, state.activeIndex) : undefined;
}
