# Docker (optional, never a prerequisite)

Companion to [SKILL.md](SKILL.md). A **container** packages the app with its runtime so a host can run it the
same way everywhere. App Creator apps run without Docker (`npm run setup`, `npm run dev`); add container files only
when the chosen host runs containers or the owner asks. Keep `npm run verify` as the main check either way.

Status: the files below are a **sketch, not built or run** from this guide. Check the current official images and
the Next.js "standalone output" documentation, build them locally, and run the main journey against the containers
before relying on them.

## What changes for containers

| Topic | Local (`npm run dev`) | Container |
|---|---|---|
| Backend bind address | `127.0.0.1` | `0.0.0.0` **inside** the container (otherwise nothing can reach it); publish the port only where needed |
| Frontend → backend | rewrite to `http://127.0.0.1:8000` | rewrite to the backend service name, e.g. `http://backend:8000` |
| When `BACKEND_URL` is read | at dev start | **at `next build`**: the scaffold's `next.config.ts` records the rewrite when building, so pass it as a build argument |
| Settings | root `.env` read by the launchers | environment variables from the host or an `env_file` that is never committed |
| Data | files in the repository folder | a volume, otherwise data disappears with the container |

## `<backend>/Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock
COPY app ./app
COPY migrations ./migrations
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Delete the `migrations` line if the app has no migrations folder. Test tools (pytest, ruff) are in the lockfile
too; that is acceptable for a course project, or split a runtime lockfile later.

## `<frontend>/Dockerfile`

Requires `output: "standalone"` in `next.config.ts` (a code change made through `build-feature`, checked by
`npm run verify`).

```dockerfile
FROM node:22-slim AS build
WORKDIR /srv
COPY package.json package-lock.json .npmrc ./
RUN npm ci
COPY . .
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-slim
WORKDIR /srv
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
COPY --from=build /srv/.next/standalone ./
COPY --from=build /srv/.next/static ./.next/static
COPY --from=build /srv/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

Delete the `public` line if the app has no `public/` folder.

## `.dockerignore` (one in each folder)

```text
node_modules
.next
.next-verify
.venv
.cache
test-results
.env
.env.*
*.db
*.sqlite3
```

The `.env` lines matter: without them a local secrets file could be copied into the image.

## `compose.yaml` at the repository root (local trial)

```yaml
services:
  backend:
    build: ./app/backend
    environment:
      DATA_MODE: fixtures            # offline, no keys; the owner sets live settings on the host
    volumes:
      - backend-data:/srv/data
  frontend:
    build:
      context: ./app/frontend
      args:
        BACKEND_URL: http://backend:8000
    ports:
      - "127.0.0.1:3000:3000"        # reachable from this computer only
    depends_on:
      - backend
volumes:
  backend-data:
```

Adjust `./app/backend` and `./app/frontend` to the config's `backendDir` and `frontendDir`. The backend has no
published port: only the frontend container reaches it, through the same-origin `/api/*` rewrite.

Try it (the owner's machine needs Docker; installing it is the owner's decision):

```bash
docker compose up --build
# open http://127.0.0.1:3000, go through the main journey, then:
docker compose down
```

## Checks before calling the containers ready

- [ ] Both images build from a fresh clone; no `.env`, database or `node_modules` inside (`docker run --rm
      <image> ls -la` on the working directory).
- [ ] The main journey works at `http://127.0.0.1:3000` in fixture mode; the error state appears when the backend
      container is stopped.
- [ ] Containers run as a non-root user.
- [ ] The README says Docker is optional and lists the commands; `npm run verify` still passes.
