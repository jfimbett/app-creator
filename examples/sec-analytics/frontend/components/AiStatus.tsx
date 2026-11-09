"use client";

import { aiStatusLine, useAiSettings } from "@/lib/ai-key";

/** The AI status in words (brief §3.1); the colour only repeats them. It never shows the key. */
export function AiStatus({ className }: { className?: string }) {
  const settings = useAiSettings();
  const tone = !settings.key ? "text-muted" : settings.lastError ? "text-negative" : settings.connectedLabel !== null ? "text-positive" : "text-fg";
  return (
    <p role="status" aria-live="polite" data-testid="ai-status" className={`min-w-0 truncate text-table ${tone} ${className ?? ""}`}>
      {aiStatusLine(settings)}
    </p>
  );
}
