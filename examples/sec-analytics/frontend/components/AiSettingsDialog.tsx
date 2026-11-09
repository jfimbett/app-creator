"use client";

import { useEffect, useId, useRef, useState } from "react";

import { AiStatus } from "@/components/AiStatus";
import { ModelPicker } from "@/components/ModelPicker";
import { ApiError } from "@/lib/api";
import { aiApi, aiErrorText } from "@/lib/ai";
import { aiKeyStore, useAiSettings } from "@/lib/ai-key";
import type { AiConnectionResponse } from "@/lib/types";

export const KEY_HELP =
  "Use your own OpenRouter key with a credit limit. Your instructor may give you a limited key for your group. This is separate from any model your coding assistant (Claude Code or Cline) uses.";
export const STORAGE_WARNING = "Scripts on this page can read browser storage; this is not secure storage";
export const CHARGE_WARNING = "This may incur a small charge";

type Test =
  | { step: "idle" }
  | { step: "confirm" }
  | { step: "running" }
  | { step: "done"; result: AiConnectionResponse }
  | { step: "failed"; message: string };

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

/**
 * AI settings (brief §3.1): the person's own key (masked, memory only unless they tick "Remember for this tab"),
 * the model, a connection test that warns about a possible charge first, the status, and Clear key.
 * A native modal dialog: the page behind it is inert, Tab stays inside, Esc closes it.
 */
export function AiSettingsDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const id = useId();
  const dialog = useRef<HTMLDialogElement>(null);
  const keyInput = useRef<HTMLInputElement>(null);
  const settings = useAiSettings();
  const [showKey, setShowKey] = useState(false);
  const [draftRemember, setDraftRemember] = useState(false);
  /** "Remember" ticked for a key that is already saved: nothing is stored until the person confirms. */
  const [pendingRemember, setPendingRemember] = useState(false);
  const [keyError, setKeyError] = useState<string | null>(null);
  const [test, setTest] = useState<Test>({ step: "idle" });
  const testController = useRef<AbortController | null>(null);

  useEffect(() => {
    const element = dialog.current;
    if (!element) return;
    if (open && !element.open) {
      element.showModal();
      keyInput.current?.focus(); // the first field, rather than the close button
    }
    if (!open && element.open) element.close();
  }, [open]);

  useEffect(() => () => testController.current?.abort(), []);

  const remember = settings.key ? settings.remember || pendingRemember : draftRemember;

  const changeRemember = (checked: boolean) => {
    if (!settings.key) setDraftRemember(checked);
    else if (checked) setPendingRemember(!settings.remember);
    else {
      setPendingRemember(false);
      aiKeyStore.setRemember(false); // removing the stored copy needs no confirmation
    }
  };

  const keepInTab = () => {
    setPendingRemember(false);
    aiKeyStore.setRemember(true);
  };

  /** The typed key is read from the field only here (the field is uncontrolled, so React never mirrors it). */
  const saveKey = () => {
    testController.current?.abort(); // a test of the previous key must not report on the new one
    const value = (keyInput.current?.value ?? "").trim();
    if (!value) {
      setKeyError("Enter your OpenRouter key first");
      return;
    }
    if (value.length > 500 || /\s/.test(value)) {
      setKeyError("A key is one word without spaces; paste it again");
      return;
    }
    setKeyError(null);
    aiKeyStore.setKey(value, { remember });
    if (keyInput.current) keyInput.current.value = "";
    setPendingRemember(false);
    setShowKey(false);
    setTest({ step: "idle" });
  };

  const runTest = async () => {
    if (!settings.key) return;
    testController.current?.abort();
    const controller = new AbortController();
    testController.current = controller;
    const version = settings.keyVersion;
    // An answer for a key that has since been replaced or cleared is ignored.
    const stale = () => controller.signal.aborted || aiKeyStore.getSnapshot().keyVersion !== version;
    setTest({ step: "running" });
    try {
      const result = await aiApi.testConnection(settings.key, { signal: controller.signal });
      if (stale()) return;
      if (result.ok) aiKeyStore.setConnected(result.label);
      else aiKeyStore.setError(result.message);
      setTest({ step: "done", result });
    } catch (error) {
      if (stale()) return;
      const message = error instanceof ApiError ? aiErrorText(error) : "The connection test failed.";
      aiKeyStore.setError(message);
      setTest({ step: "failed", message });
    }
  };

  const clearKey = () => {
    testController.current?.abort();
    aiKeyStore.clear();
    if (keyInput.current) keyInput.current.value = "";
    setDraftRemember(false);
    setPendingRemember(false);
    setKeyError(null);
    setTest({ step: "idle" });
  };

  /** Closing drops an unconfirmed "Remember" choice; nothing was stored for it. */
  const close = () => {
    setPendingRemember(false);
    onClose();
  };

  const trapTab = (event: React.KeyboardEvent<HTMLDialogElement>) => {
    if (event.key !== "Tab" || !dialog.current) return;
    const items = Array.from(dialog.current.querySelectorAll<HTMLElement>(FOCUSABLE)).filter((item) => item.offsetParent !== null);
    if (items.length === 0) return;
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  return (
    <dialog
      ref={dialog}
      aria-labelledby={`${id}-title`}
      data-testid="ai-settings"
      onCancel={(event) => {
        event.preventDefault();
        close();
      }}
      onClose={() => {
        if (open) close();
      }}
      onKeyDown={trapTab}
      className="m-auto max-h-[calc(100dvh-1rem)] w-[min(46rem,calc(100vw-1rem))] overflow-y-auto rounded-lg border border-line-strong bg-panel p-0 text-fg shadow-[var(--elev-2)] backdrop:bg-black/60"
    >
      {open ? (
        <div className="flex flex-col gap-5 p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h2 id={`${id}-title`} className="text-title font-semibold">
                AI settings
              </h2>
              <AiStatus className="mt-0.5" />
            </div>
            <button type="button" onClick={close} aria-label="Close AI settings" className="btn w-7 px-0!">
              ×
            </button>
          </div>

          <section aria-labelledby={`${id}-key-title`} className="flex flex-col gap-2">
            <h3 id={`${id}-key-title`} className="label-caps text-muted">
              Key
            </h3>
            <p id={`${id}-help`} className="text-table text-muted">
              {KEY_HELP}
            </p>
            <label htmlFor={`${id}-key`} className="text-table">
              OpenRouter key
            </label>
            <div className="flex flex-wrap gap-2">
              <input
                ref={keyInput}
                id={`${id}-key`}
                data-testid="ai-key-input"
                type={showKey ? "text" : "password"}
                autoComplete="off"
                autoCapitalize="off"
                autoCorrect="off"
                spellCheck={false}
                maxLength={500}
                defaultValue=""
                placeholder={settings.key ? "Key set; type a new key to replace it" : "Paste your key"}
                aria-describedby={`${id}-help${keyError ? ` ${id}-key-error` : ""}`}
                aria-invalid={keyError ? true : undefined}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    saveKey();
                  }
                }}
                className="field min-w-0 flex-1 font-mono placeholder:font-sans"
              />
              <button
                type="button"
                aria-pressed={showKey}
                aria-controls={`${id}-key`}
                onClick={() => setShowKey((shown) => !shown)}
                className="btn"
              >
                {showKey ? "Hide" : "Show"}
              </button>
              <button
                type="button"
                data-testid="ai-key-save"
                onClick={saveKey}
                className="btn btn-primary"
              >
                {settings.key ? "Replace key" : "Use this key"}
              </button>
            </div>
            {keyError ? (
              <p id={`${id}-key-error`} role="alert" className="text-table text-negative">
                {keyError}
              </p>
            ) : null}
            <label className="inline-flex items-center gap-2 text-table">
              <input
                type="checkbox"
                data-testid="ai-remember"
                checked={remember}
                onChange={(event) => changeRemember(event.target.checked)}
              />
              Remember for this tab (sessionStorage)
            </label>
            {remember ? (
              <div className="flex flex-wrap items-center gap-2">
                <p data-testid="ai-storage-warning" className="text-table text-warning">
                  <span className="label-caps mr-1.5">Warning</span>
                  {STORAGE_WARNING}
                </p>
                {pendingRemember ? (
                  <button type="button" onClick={keepInTab} className="btn border-warning!">
                    Keep in this tab
                  </button>
                ) : null}
              </div>
            ) : (
              <p className="text-table text-muted">The key is kept in this page&apos;s memory only and is forgotten on reload.</p>
            )}
          </section>

          <section aria-labelledby={`${id}-test-title`} className="flex flex-col gap-2">
            <h3 id={`${id}-test-title`} className="label-caps text-muted">
              Connection
            </h3>
            {test.step === "confirm" ? (
              <div data-testid="ai-charge-confirm" className="flex flex-wrap items-center gap-2 rounded-md border border-l-[3px] border-line border-l-warning bg-panel-raised px-4 py-3 text-table">
                <p className="text-warning">{CHARGE_WARNING}.</p>
                <button type="button" data-testid="ai-test-run" onClick={runTest} className="btn border-accent!">
                  Run the test
                </button>
                <button type="button" onClick={() => setTest({ step: "idle" })} className="btn">
                  Not now
                </button>
              </div>
            ) : (
              <div className="flex flex-wrap items-center gap-2 text-table">
                <button
                  type="button"
                  data-testid="ai-test"
                  disabled={!settings.key || test.step === "running"}
                  onClick={() => setTest({ step: "confirm" })}
                  className="btn"
                >
                  {test.step === "running" ? "Testing…" : "Test connection"}
                </button>
                {!settings.key ? <span className="text-muted">Save a key first.</span> : null}
              </div>
            )}
            {test.step === "done" ? (
              <p data-testid="ai-test-result" className={`text-table ${test.result.ok ? "text-positive" : "text-negative"}`}>
                {test.result.ok ? `Connected · ${test.result.label ?? "key accepted"}` : test.result.message}
                {test.result.ok ? (
                  <span className="text-fg">
                    {" · "}
                    {test.result.limit_remaining_usd === null ? "remaining limit not reported" : `$${test.result.limit_remaining_usd.toFixed(2)} limit remaining`}
                  </span>
                ) : null}
              </p>
            ) : null}
            {test.step === "failed" ? (
              <p data-testid="ai-test-result" role="alert" className="text-table text-negative">
                {test.message}
              </p>
            ) : null}
          </section>

          <ModelPicker apiKey={settings.key} keyVersion={settings.keyVersion} selected={settings.model} onChoose={(model) => aiKeyStore.setModel(model)} />

          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-line pt-4">
            <button
              type="button"
              data-testid="ai-clear"
              onClick={clearKey}
              disabled={!settings.key && !settings.model}
              className="btn btn-danger"
            >
              Clear key
            </button>
            <button type="button" onClick={close} className="btn px-4!">
              Done
            </button>
          </div>
        </div>
      ) : null}
    </dialog>
  );
}
