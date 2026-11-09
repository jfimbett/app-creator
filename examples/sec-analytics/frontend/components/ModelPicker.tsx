"use client";

import { useCallback, useId, useState } from "react";

import { StatePanel } from "@/components/StatePanel";
import { aiApi, aiErrorText, filterModels, formatContextLength, formatUsdPerMillion, isValidModelId } from "@/lib/ai";
import type { AiModelsResponse } from "@/lib/types";
import { useApiResource } from "@/lib/useApiResource";

type Props = {
  apiKey: string | null;
  keyVersion: number;
  selected: string | null;
  onChoose: (id: string) => void;
};

const NO_MODELS: AiModelsResponse = { models: [], fetched_at: "" };

/**
 * The model choice: the live list from OpenRouter (through /api/ai/models, only once a key is set) as a dense,
 * filterable table, and a manual id field. Nothing is preselected and there is no default model.
 */
export function ModelPicker({ apiKey, keyVersion, selected, onChoose }: Props) {
  const id = useId();
  const [filter, setFilter] = useState("");
  const [manual, setManual] = useState("");
  const [manualError, setManualError] = useState<string | null>(null);

  const load = useCallback((signal: AbortSignal) => (apiKey ? aiApi.listModels(apiKey, { signal }) : Promise.resolve(NO_MODELS)), [apiKey]);
  const list = useApiResource(`ai-models:${keyVersion}`, load);
  const shown = list.status === "ok" ? filterModels(list.data.models, filter) : [];

  const chooseManual = () => {
    const value = manual.trim();
    if (!isValidModelId(value)) {
      setManualError("Use 1–200 letters, digits or . _ : / - (for example provider/model-name)");
      return;
    }
    setManualError(null);
    setManual("");
    onChoose(value);
  };

  return (
    <fieldset className="flex min-w-0 flex-col gap-2">
      <legend className="label-caps mb-1 text-muted">Model</legend>
      <p data-testid="model-choice" className="text-table">
        {selected ? (
          <>
            Chosen: <span className="code-id [overflow-wrap:anywhere]">{selected}</span>
          </>
        ) : (
          <span className="text-warning">No model chosen yet. Ask stays disabled until you choose one.</span>
        )}
      </p>

      {!apiKey ? (
        <p className="text-table text-muted">Enter and save a key to load the model list.</p>
      ) : list.status === "loading" ? (
        <StatePanel kind="loading" title="Loading models from OpenRouter…" rows={4} />
      ) : list.status === "error" ? (
        <StatePanel kind="error" title="Model list not loaded" message={aiErrorText(list.error)} reference={list.error.reference} action={{ label: "Try again", onClick: list.reload }} />
      ) : (
        <>
          <label htmlFor={`${id}-filter`} className="flex flex-col gap-1 text-table">
            <span className="text-muted">Filter models by id or name</span>
            <input
              id={`${id}-filter`}
              data-testid="model-filter"
              type="search"
              autoComplete="off"
              spellCheck={false}
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
              className="field"
            />
          </label>
          {/* `relative` keeps the sr-only caption inside this scroll box, so it cannot widen the page. */}
          <div className="table-box relative max-h-64">
            <table data-testid="model-table" className="data-table">
              <caption className="sr-only">Models from OpenRouter; prices in USD per million tokens</caption>
              <thead>
                <tr>
                  <th scope="col">Model</th>
                  <th scope="col" className="num">
                    Context
                  </th>
                  <th scope="col" className="num">
                    Prompt $/M
                  </th>
                  <th scope="col" className="num">
                    Completion $/M
                  </th>
                  <th scope="col">Expiry</th>
                </tr>
              </thead>
              <tbody>
                {shown.map((model) => (
                  <tr key={model.id} data-testid="model-row" data-model-id={model.id} aria-selected={model.id === selected}>
                    <td className="max-w-[16rem]">
                      <label className="flex cursor-pointer items-center gap-2">
                        <input type="radio" name={`${id}-model`} value={model.id} checked={model.id === selected} onChange={() => onChoose(model.id)} />
                        <span className="flex min-w-0 flex-col leading-tight">
                          <span className="code-id truncate">{model.id}</span>
                          <span className="truncate text-label text-muted">{model.name}</span>
                        </span>
                      </label>
                    </td>
                    <td className="num">{formatContextLength(model.context_length)}</td>
                    <td className={`num ${model.prompt_usd_per_million === null ? "text-muted" : ""}`}>{formatUsdPerMillion(model.prompt_usd_per_million)}</td>
                    <td className={`num ${model.completion_usd_per_million === null ? "text-muted" : ""}`}>{formatUsdPerMillion(model.completion_usd_per_million)}</td>
                    <td className="text-warning">{model.expiration_date ? `expires ${model.expiration_date}` : ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {shown.length === 0 ? <p className="px-2 py-1.5 text-table text-muted">{filter.trim() ? "No model matches the filter" : "OpenRouter listed no models"}</p> : null}
          </div>
        </>
      )}

      <div className="flex flex-col gap-1 text-table">
        <label htmlFor={`${id}-manual`} className="text-muted">
          Or type a model id
        </label>
        <div className="flex flex-wrap gap-2">
          <input
            id={`${id}-manual`}
            data-testid="model-manual"
            type="text"
            autoComplete="off"
            spellCheck={false}
            maxLength={200}
            value={manual}
            aria-invalid={manualError ? true : undefined}
            aria-describedby={manualError ? `${id}-manual-error` : undefined}
            onChange={(event) => setManual(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                chooseManual();
              }
            }}
            className="field min-w-0 flex-1 font-mono"
          />
          <button type="button" onClick={chooseManual} className="btn">
            Use this id
          </button>
        </div>
        {manualError ? (
          <p id={`${id}-manual-error`} role="alert" className="text-negative">
            {manualError}
          </p>
        ) : null}
      </div>
    </fieldset>
  );
}
