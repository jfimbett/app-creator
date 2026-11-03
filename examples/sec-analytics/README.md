# SEC Analytics (example app)

> **Stub (milestone M1 in progress).** Later M1 steps fill in this README: the demo universe, how to run the demo,
> where the fixtures come from, how to recapture them, and the milestone status.

SEC Analytics is the worked example of App Creator: a dark, terminal-style web app for reading public company
data from the SEC (U.S. Securities and Exchange Commission). Milestone M1 runs offline only, on recorded SEC data
for three demo companies: Apple, Microsoft and Alphabet.

- Code: `frontend/` (Next.js) and `backend/` (FastAPI).
- Planning documents: `milestones/` at the repository root (product, architecture, acceptance, plan).

## Run it (from the repository root)

```bash
npm run setup    # once: installs the backend and frontend packages
npm run demo     # offline demo on recorded data
npm run verify   # every check
```
