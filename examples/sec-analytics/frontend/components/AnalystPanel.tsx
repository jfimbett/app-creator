"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";

import { AiSettingsDialog } from "@/components/AiSettingsDialog";
import { AiStatus } from "@/components/AiStatus";
import { SourceChips } from "@/components/SourceChips";
import { StatePanel } from "@/components/StatePanel";
import { ApiError } from "@/lib/api";
import { aiApi, aiErrorText, aiNextStep, CANCELLED, LENGTH_CUT, NOT_IN_SOURCES, QUESTION_MAX, usageLine } from "@/lib/ai";
import { aiKeyStore, useAiSettings } from "@/lib/ai-key";
import { useDataSource } from "@/lib/source";
import type { AiChatResponse, AiScope } from "@/lib/types";
import { useApiResource } from "@/lib/useApiResource";

export const NOT_CONFIGURED = "AI not configured: add your own OpenRouter key";

type Run =
  | { status: "idle" }
  | { status: "running" }
  | { status: "done"; response: AiChatResponse }
  | { status: "failed"; error: ApiError }
  | { status: "cancelled" };

/** The error codes that say something about the key itself, so the status line shows them. */
const KEY_PROBLEMS = new Set(["ai_key_invalid", "ai_key_missing", "ai_insufficient_credits", "ai_forbidden"]);

function InfoIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 16 16" className="mt-0.5 h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="8" cy="8" r="6.5" />
      <path d="M8 7v4.5M8 4.6v.1" strokeLinecap="round" />
    </svg>
  );
}

function Answer({ response }: { response: AiChatResponse }) {
  if (response.refusal) {
    return (
      <div data-testid="ai-refusal" data-code={response.refusal.code} className="border-l-2 border-l-warning bg-panel-raised px-3 py-2">
        <p className="flex flex-wrap items-baseline gap-x-2">
          <span className="label-caps text-warning">Not answered</span>
          <span className="text-fg">{response.refusal.message}</span>
        </p>
        <p className="mt-1 text-table text-muted">Ask about the loaded SEC figures or filing text instead.</p>
      </div>
    );
  }
  const usage = usageLine(response.usage);
  return (
    <div className="flex flex-col gap-2">
      {/* Plain text only: the model's answer becomes a React text node, never HTML or Markdown. */}
      <p data-testid="ai-answer" className="whitespace-pre-wrap text-[14px] leading-[1.6] text-fg [overflow-wrap:anywhere]">
        {response.answer}
      </p>
      {response.finish_reason === "length" ? (
        <p data-testid="ai-cut" className="text-table text-warning">
          <span className="label-caps mr-1.5">Cut</span>
          {LENGTH_CUT}
        </p>
      ) : null}
      <SourceChips citations={response.citations} />
      {response.citation_note ? (
        <p data-testid="ai-citation-note" className="text-table text-warning">
          {response.citation_note}
        </p>
      ) : null}
      {response.invalid_references.length > 0 ? (
        <div data-testid="ai-invalid-refs" className="text-table">
          <p className="text-warning">{NOT_IN_SOURCES}</p>
          <ul className="mt-0.5 flex flex-wrap gap-1.5">
            {response.invalid_references.map((reference) => (
              <li key={reference} className="code-id rounded-sm border border-dashed border-line px-1.5 text-muted line-through">
                [{reference}]
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      <p data-testid="ai-notice" className="flex gap-1.5 text-table text-muted">
        <InfoIcon />
        <span>{response.notice}</span>
      </p>
      <p data-testid="ai-usage" className="text-label text-muted [overflow-wrap:anywhere]">
        Model <span className="code-id">{response.model}</span>
        {usage ? ` · ${usage}` : ""}
      </p>
    </div>
  );
}

type Props = { scope: AiScope; onClose: () => void };

/**
 * The analyst (brief §3.2): a side panel next to the page on wide screens, a full-screen sheet on phones.
 * It answers one question at a time about the current scope, from data the server selects, with checked
 * source chips. Without a key it says so and every other feature of the page is unchanged.
 */
export function AnalystPanel({ scope, onClose }: Props) {
  const id = useId();
  const settings = useAiSettings();
  const { source } = useDataSource();
  const [question, setQuestion] = useState("");
  const [run, setRun] = useState<Run>({ status: "idle" });
  /** The scope and source the last question was asked for; its answer is hidden once the page's scope changes. */
  const [askedFor, setAskedFor] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const controller = useRef<AbortController | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  const settingsButton = useRef<HTMLButtonElement>(null);

  const scopeKey = JSON.stringify(scope);
  const loadContext = useCallback((signal: AbortSignal) => aiApi.context(JSON.parse(scopeKey) as AiScope, source, { signal }), [scopeKey, source]);
  const contextKey = `${scopeKey}:${source}`;
  const context = useApiResource(`ai-context:${contextKey}`, loadContext);

  useEffect(() => {
    heading.current?.focus({ preventScroll: true });
    return () => controller.current?.abort();
  }, []);

  const running = run.status === "running";
  const current = askedFor === contextKey || running ? run : ({ status: "idle" } as Run);
  const trimmed = question.trim();
  const configured = Boolean(settings.key);
  const canAsk = configured && Boolean(settings.model) && !running && trimmed.length >= 1 && question.length <= QUESTION_MAX;

  const ask = async () => {
    if (!canAsk || !settings.key || !settings.model) return;
    const request = new AbortController();
    controller.current = request;
    setAskedFor(contextKey);
    setRun({ status: "running" });
    try {
      const response = await aiApi.chat(settings.key, { model: settings.model, scope, question: trimmed, source }, { signal: request.signal });
      if (settings.lastError) aiKeyStore.setError(null);
      setRun({ status: "done", response });
    } catch (error) {
      if (request.signal.aborted) {
        setRun({ status: "cancelled" });
        return;
      }
      const failure =
        error instanceof ApiError
          ? error
          : new ApiError(null, { error: { code: "client_error", message: "The page could not read the answer.", details: null, reference: null } });
      if (KEY_PROBLEMS.has(failure.code)) aiKeyStore.setError(failure.message);
      setRun({ status: "failed", error: failure });
    } finally {
      if (controller.current === request) controller.current = null;
    }
  };

  const cancel = () => controller.current?.abort();

  const closeSettings = () => {
    setSettingsOpen(false);
    settingsButton.current?.focus();
  };

  return (
    <aside
      id="analyst-panel"
      aria-labelledby={`${id}-title`}
      data-testid="analyst-panel"
      onKeyDown={(event) => {
        if (event.key === "Escape" && !settingsOpen) {
          event.stopPropagation();
          onClose();
        }
      }}
      className="fixed inset-0 z-40 flex flex-col overflow-hidden bg-panel xl:sticky xl:inset-auto xl:top-14 xl:z-auto xl:h-[calc(100dvh-4.5rem)] xl:self-start xl:w-[400px] xl:shrink-0 xl:border xl:border-line"
    >
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 border-b border-line px-3 py-2">
        <h2 id={`${id}-title`} ref={heading} tabIndex={-1} className="label-caps text-fg">
          Analyst
        </h2>
        <AiStatus className="flex-1" />
        <div className="ml-auto flex items-center gap-1.5">
          <button
            ref={settingsButton}
            type="button"
            data-testid="ai-settings-open"
            onClick={() => setSettingsOpen(true)}
            className="rounded-sm border border-line px-2 py-0.5 text-table text-fg hover:border-accent"
          >
            AI settings
          </button>
          <button type="button" data-testid="analyst-close" aria-label="Close analyst" onClick={onClose} className="rounded-sm border border-line px-2 py-0.5 text-fg hover:border-accent">
            ×
          </button>
        </div>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-3">
        <p data-testid="ai-context" className="font-mono text-table text-muted [overflow-wrap:anywhere]">
          {context.status === "ok" ? context.data.line : context.status === "loading" ? "Context: loading…" : `Context not available: ${context.error.message}`}
        </p>

        {!configured ? (
          <div data-testid="ai-not-configured" className="border-l-2 border-l-line bg-panel-raised px-3 py-2">
            <p className="font-semibold text-fg">{NOT_CONFIGURED}</p>
            <p className="mt-1 text-muted">The analyst uses your own OpenRouter key. Everything else in the app works without one.</p>
            <button
              type="button"
              onClick={() => setSettingsOpen(true)}
              className="mt-2 rounded-sm border border-line bg-panel px-2 py-1 text-fg hover:border-accent"
            >
              AI settings
            </button>
          </div>
        ) : (
          <form
            className="flex flex-col gap-1.5"
            onSubmit={(event) => {
              event.preventDefault();
              void ask();
            }}
          >
            <label htmlFor={`${id}-question`} className="text-table">
              Question about this data
            </label>
            <textarea
              id={`${id}-question`}
              data-testid="ai-question"
              rows={3}
              maxLength={QUESTION_MAX}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
                  event.preventDefault();
                  void ask();
                }
              }}
              aria-describedby={`${id}-count${settings.model ? "" : ` ${id}-need-model`}`}
              className="resize-y rounded-sm border border-line bg-bg px-2 py-1.5 text-fg placeholder:text-muted focus:border-accent focus:outline-none"
              placeholder="For example: Why did net margin change?"
            />
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span id={`${id}-count`} data-testid="ai-count" className="text-label tabular-nums text-muted">
                {question.length.toLocaleString("en-US")} / {QUESTION_MAX.toLocaleString("en-US")} characters
              </span>
              <div className="flex gap-1.5">
                {running ? (
                  <button type="button" data-testid="ai-cancel" onClick={cancel} className="rounded-sm border border-line px-3 py-1 text-table text-fg hover:border-accent">
                    Cancel
                  </button>
                ) : null}
                <button
                  type="submit"
                  data-testid="ai-ask"
                  disabled={!canAsk}
                  className="rounded-sm border border-accent bg-accent px-3 py-1 text-table font-semibold text-on-accent disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {running ? "Asking…" : "Ask"}
                </button>
              </div>
            </div>
            {!settings.model ? (
              <p id={`${id}-need-model`} className="text-table text-warning">
                Choose a model in AI settings to ask.
              </p>
            ) : (
              <p className="text-label text-muted [overflow-wrap:anywhere]">
                Model <span className="code-id">{settings.model}</span>
              </p>
            )}
          </form>
        )}

        <div aria-live="polite" className="flex flex-col gap-2">
          {current.status === "running" ? <StatePanel kind="loading" title="Waiting for the AI (up to 60 s)…" rows={4} /> : null}
          {current.status === "cancelled" ? (
            <p data-testid="ai-cancelled" role="status" className="border-l-2 border-l-line bg-panel-raised px-3 py-2 text-table">
              <span className="label-caps mr-2 text-muted">Stopped</span>
              {CANCELLED}. Ask again when ready.
            </p>
          ) : null}
          {current.status === "failed" ? (
            <div data-testid="ai-error" data-code={current.error.code}>
              <StatePanel kind="error" title={aiErrorText(current.error)} message={aiNextStep(current.error.code)} reference={current.error.reference} />
            </div>
          ) : null}
          {current.status === "done" ? <Answer response={current.response} /> : null}
        </div>
      </div>

      <AiSettingsDialog open={settingsOpen} onClose={closeSettings} />
    </aside>
  );
}
