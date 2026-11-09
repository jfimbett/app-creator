/**
 * The app's mark: three rising bars, the same drawing as app/icon.svg, in theme colours (accent bars on a panel tile).
 * Decorative: the brand name next to it carries the meaning.
 */
export function BrandMark({ size = 24 }: { size?: number }) {
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 32 32" className="shrink-0">
      <rect width="32" height="32" rx="7" fill="var(--panel-raised)" stroke="var(--border-strong)" strokeWidth="1" />
      <path d="M7 24V15h4v9zm7 0V8h4v16zm7 0v-6h4v6z" fill="var(--accent)" />
    </svg>
  );
}
