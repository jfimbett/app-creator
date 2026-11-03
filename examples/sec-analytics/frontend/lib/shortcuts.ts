// Pure logic for the global "focus search" shortcuts: "/" and Ctrl-K or Cmd-K.

/** True if the element accepts typed text (input, textarea, select or contenteditable). */
function isEditable(target: EventTarget | null): boolean {
  if (!(target instanceof Element)) return false;
  if (["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return true;
  return target.closest('[contenteditable=""], [contenteditable="true"], [contenteditable="plaintext-only"]') !== null;
}

/**
 * Decides whether a keydown should move focus to the search box `searchInput`.
 * - "/" (no Ctrl, Cmd or Alt) counts only outside text fields, so it can still be typed.
 * - Ctrl-K or Cmd-K counts anywhere except inside another text field; inside the search box itself it
 *   is kept (and the caller prevents the browser's own Ctrl-K).
 */
export function isFocusSearchShortcut(event: KeyboardEvent, searchInput: Element | null): boolean {
  if (event.isComposing || event.altKey) return false;
  const target = event.target;
  if (event.key === "/") {
    return !event.ctrlKey && !event.metaKey && !isEditable(target);
  }
  if (event.key.toLowerCase() === "k" && (event.ctrlKey || event.metaKey) && !event.shiftKey) {
    return target === searchInput || !isEditable(target);
  }
  return false;
}
