// The message printed by the root commands when no app is configured yet (template mode).
import { c } from './lib.mjs';

export function printTemplateGuidance(command) {
  console.log(`
${c.bold('No app is configured yet')} (app-creator.config.json has "app": null), so \`npm run ${command}\` has nothing to run.

Two ways to start:

  1. Create the walking skeleton (a tiny working Next.js + FastAPI app), then shape it:
       npm run create-app          copies scaffold/ to app/ and points the config at it
       npm run setup               installs its packages (Python .venv, node_modules, test browser)
       npm run dev                 opens it at http://127.0.0.1:3000

  2. Start from your idea: open Claude Code in this folder and type
       /product-interview
     It asks about your product, writes the documents, and then creates the app the same way.

More: START-HERE.md and docs/TOOLKIT.md.`);
}
