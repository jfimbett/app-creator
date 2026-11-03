# Stack versions: checking the D5/D6 pins

Retrieved 2026-11-03. Every claim below gives its source. "npm" means `npm view <pkg> time|engines|peerDependencies` and "PyPI" means `https://pypi.org/pypi/<pkg>/json`, both queried on 2026-11-03. The rule being checked comes from D5: use the newest stable release that is at least 2 weeks old (released on or before 2026-10-20).

## Verdict per pin

| Pin | Status | Evidence |
|---|---|---|
| next 16.4.2 | OK (released 2026-10-15; 16.4.3 came out 2026-10-23 and is too new) | npm |
| react / react-dom 19.3.1 | OK (released 2026-10-14) | npm |
| tailwindcss 4.3.3 | OK (released 2026-07-16; 4.3.4 came out 2026-11-02) | npm |
| recharts 3.10.1 | OK (released 2026-07-25). Its peers accept React `^19.0.0` | npm |
| @playwright/test 1.64.1 | OK (released 2026-10-14) | npm |
| typescript 6.0.3 | **Keep it, but change the reason** (see TypeScript below) | npm |
| eslint 10.13.0 | OK (released 2026-10-16) | npm |
| eslint-config-next 16.4.2 | OK. It must stay equal to `next` | npm |
| vitest 4.1.12 | **Breaks the D5 rule**: 5.0.5 (2026-10-15) qualifies. See Vitest | npm |
| fastapi 0.150.0 | OK (released 2026-10-19; 0.151+ all came out 2026-10-20 or later) | PyPI |
| uvicorn 0.54.0 | OK (released 2026-09-25, still the latest) | PyPI |
| httpx, respx, beautifulsoup4, pydantic 2.14.1, pytest 9.1.1, ruff 0.17.1 | OK (each is the latest, or the newer release is under 2 weeks old) | PyPI |
| Python 3.10–3.13 | OK. fastapi, uvicorn, pydantic and pytest require `>=3.10` and also list 3.14 in their classifiers | PyPI |

**Missing pins to add to D5:**
- `@tailwindcss/postcss` 4.3.3, matching tailwindcss.
- `postcss`.
- `react-is` 19.3.1. Recharts lists it as a peer, and it must match the installed React version.
- The Vitest helper packages (see Vitest).

## 1. Next.js 16

- **Node:** the minimum is 20.9.0, and "Node.js 18 no longer supported". Sources: https://nextjs.org/docs/app/getting-started/installation and https://nextjs.org/docs/app/guides/upgrading/version-16. The npm `engines` field agrees: `>=20.9.0`.
- **TypeScript:** the minimum is `v5.1.0` (installation page, as above), so TypeScript 6 is supported. The TypeScript config page now has a **"Using TypeScript 7"** section: "TypeScript 7 does not currently provide the JavaScript compiler API". Next uses "the project-local `tsc` CLI by default". The option `experimental.useTypeScriptCli` switches that behaviour. Source: https://nextjs.org/docs/app/api-reference/config/typescript.
  - **This removes D5's stated reason for avoiding TS 7.** The real blocker is in npm metadata: `eslint-config-next` depends on `typescript-eslint ^8.56.0`, and the latest typescript-eslint (8.72.1) has peer `typescript >=4.8.4 <6.1.0`. TS 7.0.2 (released 2026-07-08) would break the lint toolchain. **Keep 6.0.3, and give typescript-eslint's peer range as the reason.**
- **React:** the docs give no numeric minimum. The npm peer range for `next` is `react ^18.2.0 || ^19.0.0`. The upgrade guide says to add `@types/react` and `@types/react-dom`.
- **Rewrites for /api:**
  ```js
  async rewrites() { return [{ source: '/api/:path*', destination: 'http://127.0.0.1:8000/api/:path*' }] }
  ```
  - Plain array rewrites run after the filesystem check and before dynamic routes. A real `app/api/...` route therefore takes precedence over the rewrite, so don't create any. Source: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites.
  - The page does **not** say whether rewrites behave differently under `next dev` and `next start`. [unverified] We expect them to work in both, because rewrites are a server feature. Smoke-test both modes with Playwright.
- **distDir:** the path is resolved relative to `next.config`. Next "takes ownership of `distDir` and will sometimes delete its contents". Next fails with "Invalid distDir" if the path resolves outside the app/workspace or to the app directory or one of its ancestors. Source: https://nextjs.org/docs/app/api-reference/config/next-config-js/distDir.
  - Since v16, `next dev` writes to `.next/dev`, separate from build output (upgrade guide). How a custom distDir interacts with that subfolder is not documented [unverified].
- **Lint:** "Starting with Next.js 16, `next lint` is removed", and `next build` "no longer runs the linter automatically". Use `"lint": "eslint"`. Source: https://nextjs.org/docs/app/api-reference/config/eslint. Flat config, `eslint.config.mjs`:
  ```js
  import { defineConfig, globalIgnores } from 'eslint/config'
  import nextVitals from 'eslint-config-next/core-web-vitals'
  import nextTs from 'eslint-config-next/typescript'
  export default defineConfig([...nextVitals, ...nextTs,
    globalIgnores(['.next/**', 'out/**', 'build/**', 'next-env.d.ts'])])
  ```
  The codemod is `npx @next/codemod@canary next-lint-to-eslint-cli .`. eslint 10's engines field is `^20.19.0 || ^22.13.0 || >=24` (npm). That is a higher Node floor than Next's.
- **Turbopack:** it is the default for both `next dev` and `next build`. Opt out with `--webpack`. A custom `webpack` config makes `next build` fail unless you pass `--webpack`. Sources: https://nextjs.org/docs/app/api-reference/turbopack and the CLI page.

## 2. Tailwind v4 and shadcn/ui

- **Tailwind:** run `npm install tailwindcss @tailwindcss/postcss postcss`. Then use `postcss.config.mjs` → `export default { plugins: { "@tailwindcss/postcss": {} } }` and add `@import "tailwindcss";` to `app/globals.css`. No `tailwind.config.js` is needed. Source: https://tailwindcss.com/docs/installation/framework-guides/nextjs.
- **shadcn:**
  - The commands are `npx shadcn@latest init` (`-t next` for a new app) and then `npx shadcn@latest add button`. Source: https://ui.shadcn.com/docs/installation/next.
  - "All components are updated for Tailwind v4 and React 19", and `tailwindcss-animate` has been replaced by `tw-animate-css`. Source: https://ui.shadcn.com/docs/tailwind-v4.
  - **Non-interactive runs are possible.** `init` takes `-y/--yes` ("default: true"), `-d/--defaults` (`--template=next --preset=nova`), `-f`, `-c/--cwd`, `-s/--silent`, `-t`, `-p`. `add` takes `-y`, `-o/--overwrite`, `-c`, `-a`, `-p/--path`, `-s`, `--dry-run`. There is **no `--base-color` flag**. Source: https://ui.shadcn.com/docs/cli.
  - The CLI is the npm package `shadcn`, currently 4.23.0 (2026-10-27, too new under the 2-week rule). Its engines field is `node >=20.18.1` (npm). Pin it, for example `npx shadcn@<pinned>`.
  - **A manual path also exists:**
    - Install with `add shadcn class-variance-authority cn lucide-react tw-animate-css`.
    - `lib/utils.ts` contains `export { cn } from "cn"`. Note: the current manual docs use the `cn` package, not clsx plus tailwind-merge.
    - The CSS imports are `tailwindcss`, `tw-animate-css` and `shadcn/tailwind.css`.
    - In `components.json`, `tailwind.config` is `""` for v4. The example uses `"style": "base-nova"`.
    - Sources: https://ui.shadcn.com/docs/installation/manual and https://ui.shadcn.com/docs/components-json.
  - The older "new-york is the default" notes are outdated; current defaults are nova/base-nova.
- Recommendation: run `shadcn add -y -o -c <app>` once at template-creation time, commit the generated `components/ui/` files, and never call the CLI at student install time.

## 3. Recharts 3 and React 19

- The installation guide only says `npm install recharts`. Source: https://recharts.github.io/en-US/guide/installation/.
- The README says `npm install recharts react-is` and "`react-is` needs to match the version of your installed `react` package". Source: https://github.com/recharts/recharts/blob/main/README.md.
- The 3.0 migration guide gives the minimum as React 16.8. Source: https://github.com/recharts/recharts/wiki/3.0-migration-guide.
- No docs page explicitly says "React 19". The npm peers for 3.10.1 are `react`, `react-dom` and `react-is` with `^19.0.0` (npm). Pin `react-is` 19.3.1. Recharts components are client-only, so use them in `"use client"` files.

## 4. Playwright

- `PLAYWRIGHT_BROWSERS_PATH=<dir>` downloads browsers to that directory, and the same variable on `npx playwright test` makes Playwright look there. The docs show it at both steps, so set it for both. `PLAYWRIGHT_BROWSERS_PATH=0` installs into `node_modules/playwright-core/.local-browsers` (hermetic). The macOS default is `~/Library/Caches/ms-playwright`. Source: https://playwright.dev/docs/browsers.
- Browser-name installs are documented. The page's examples are `webkit` and `--with-deps chromium`, so `chromium` follows the same pattern. Headless runs use **chromium headless shell** by default. `--only-shell` skips the full Chromium when no `channel` is set, and `--no-shell` does the opposite. For a small local install: `PLAYWRIGHT_BROWSERS_PATH=<project>/.playwright-browsers npx playwright install --only-shell chromium`. Do **not** use `--with-deps` on macOS; it is aimed at Linux CI. Source: same page.
- System requirements are "Node.js: latest 22.x, 24.x or 26.x" and "macOS 14 (Sonoma) or later". The npm engines field says `>=20`. Source: https://playwright.dev/docs/intro.
- `webServer` options:
  - `command`
  - `url`, which counts as ready on a 2xx, 3xx, 400, 401, 402 or 403 response. `port` is deprecated.
  - `reuseExistingServer` (the docs recommend `!process.env.CI`)
  - `timeout` (default 60000)
  - `cwd` (defaults to the config file's directory)
  - `env` (inherits plus `PLAYWRIGHT_TEST=1`)
  - `stdout` (default `ignore`)
  - `gracefulShutdown` (`{signal:'SIGTERM',timeout:500}`; otherwise SIGKILL)
  - `name`
  - **An array is supported**, so you can start both FastAPI and `next start`.
  Source: https://playwright.dev/docs/test-webserver.

## 5. FastAPI and uvicorn

- The FastAPI docs show no Python version in the text, only a PyPI badge. Source: https://fastapi.tiangolo.com/. PyPI says `requires_python >=3.10`, with classifiers for 3.10 through 3.14.
- Install `"fastapi[standard]"` (in quotes). `fastapi dev` auto-reloads, and `fastapi run` is the production server. Both run Uvicorn. Sources: https://fastapi.tiangolo.com/ and https://fastapi.tiangolo.com/deployment/manually/.
- Uvicorn: run `uvicorn main:app --host ... --port ...`. `uvicorn[standard]` adds extras such as uvloop. `--reload` is for development only. Source: the FastAPI manual-deployment page.
- https://www.uvicorn.org/ **could not be fetched** (DNS failure). The uvicorn docs themselves are [unverified]. PyPI gives `requires_python >=3.10`.

## 6. Vitest

- The current guide is for **v5.1.0**: "Vitest requires Vite >=v6.4.0 and Node >=v22.12.0". Source: https://vitest.dev/guide/. npm: vitest 4.1.12 supports Node `^20 || ^22 || >=24`, and 5.x requires `^22.12 || ^24 || >=26`.
- Next's recipe installs `vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/dom vite-tsconfig-paths`. Its `vitest.config.mts` uses `plugins: [tsconfigPaths(), react()]` and `test.environment: 'jsdom'`. Async Server Components are not supported, so test them end-to-end. Source: https://nextjs.org/docs/app/guides/testing/vitest.
- `@vitejs/plugin-react` 6.2.1 requires `vite ^8` (npm). Pin `vite` 8.x explicitly.

## Recommended changes

1. **Vitest:** follow the D5 rule and move to **vitest 5.0.5**, and **raise the Node floor to 22.12**. Playwright's documented support is already 22/24/26, so Node 20 can't be tested end-to-end anyway. Alternatively, keep 4.1.12 and record the rule exception and the reason (Node 20 support).
2. **TypeScript:** keep 6.0.3, but change the reason to "typescript-eslint peer `<6.1.0`".
3. Add pins for `@tailwindcss/postcss` 4.3.3, `postcss`, `react-is` 19.3.1, `@types/react`/`@types/react-dom`, `vite`, `@vitejs/plugin-react`, `jsdom`, `@testing-library/*`, `vite-tsconfig-paths` and the `shadcn` CLI. Choose versions with the same npm `time` check.
4. D6 Python 3.10–3.13 is valid. 3.14 is declared by the core packages but not by httpx's classifiers (they stop at 3.12; its `requires_python` is `>=3.8`). Keep 3.13 as the tested ceiling.
5. **Environment warning:** on this machine `python3` is **3.9.19**, below the 3.10 floor, and no `python3.1x` is on PATH. Node is v22.14.0, which meets every floor above. The launcher must detect a suitable Python or tell the user to install one.
