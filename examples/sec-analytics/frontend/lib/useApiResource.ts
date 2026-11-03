"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "./api";

/** What a screen shows for one API call: still loading, the data, or the error envelope. */
export type Resource<T> =
  | { status: "loading" }
  | { status: "ok"; data: T }
  | { status: "error"; error: ApiError };

type Settled<T> = { key: string } & ({ status: "ok"; data: T } | { status: "error"; error: ApiError });

function asApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;
  return new ApiError(null, {
    error: { code: "client_error", message: "The page could not read the answer.", details: null, reference: null },
  });
}

/**
 * Runs `load` whenever `key` changes (and on `reload`), cancelling the previous request.
 * `load` must be stable for a given key (wrap it in useCallback).
 */
export function useApiResource<T>(key: string, load: (signal: AbortSignal) => Promise<T>): Resource<T> & { reload: () => void } {
  const [attempt, setAttempt] = useState(0);
  const [settled, setSettled] = useState<Settled<T> | null>(null);
  const requestKey = `${key}#${attempt}`;

  useEffect(() => {
    const controller = new AbortController();
    load(controller.signal).then(
      (data) => setSettled({ key: requestKey, status: "ok", data }),
      (error: unknown) => {
        if (controller.signal.aborted) return;
        setSettled({ key: requestKey, status: "error", error: asApiError(error) });
      },
    );
    return () => controller.abort();
  }, [requestKey, load]);

  const reload = useCallback(() => setAttempt((n) => n + 1), []);

  if (!settled || settled.key !== requestKey) return { status: "loading", reload };
  return settled.status === "ok" ? { status: "ok", data: settled.data, reload } : { status: "error", error: settled.error, reload };
}
