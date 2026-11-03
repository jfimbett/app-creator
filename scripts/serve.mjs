// Shared by dev.mjs and demo.mjs: starts the backend and frontend, prints the URL, stops both on Ctrl+C.
import { setupProblems, startApp } from './app-tasks.mjs';
import { printTemplateGuidance } from './guidance.mjs';
import { c, checkNode, fail, heading, isStopping, loadConfig, requireFreePort, stopServices } from './lib.mjs';

/** mode: 'dev' (config.devEnv) or 'demo' (config.demoEnv). */
export async function serve(mode) {
  checkNode();
  const { app } = loadConfig();
  if (!app) {
    printTemplateGuidance(mode);
    process.exit(0);
  }
  const problems = setupProblems(app);
  if (problems.length) fail(`setup has not been run: ${problems.join('; ')}.\n  Run \`npm run setup\` first.`);

  await requireFreePort(app.ports.backend, 'BACKEND_PORT', 'backend');
  await requireFreePort(app.ports.frontend, 'FRONTEND_PORT', 'frontend');

  const extraEnv = mode === 'demo' ? app.demoEnv : app.devEnv;
  heading(`Starting ${app.name} (${mode === 'demo' ? 'demo mode' : 'development mode'})`);
  if (Object.keys(extraEnv).length) console.log(c.dim(`Settings from config ${mode}Env: ${Object.keys(extraEnv).join(', ')}`));
  try {
    const { url, backend, frontend } = await startApp(app, {
      backendPort: app.ports.backend, frontendPort: app.ports.frontend, mode: 'dev', extraEnv,
    });
    console.log(`\n${c.green(c.bold(`${app.name} is running: ${url}`))}`);
    console.log(c.dim(`(backend on http://127.0.0.1:${app.ports.backend}; press Ctrl+C to stop both)`));
    const which = await Promise.race([backend.exited.then(() => 'backend'), frontend.exited.then(() => 'frontend')]);
    if (isStopping()) return; // Ctrl+C: the signal handler stops everything and exits.
    console.error(c.red(`\nThe ${which} stopped unexpectedly; stopping the other one.`));
    await stopServices();
    process.exit(1);
  } catch (err) {
    await stopServices();
    fail(err.message);
  }
}
