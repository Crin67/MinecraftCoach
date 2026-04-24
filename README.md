# Minecraft Coach

Minecraft Coach is a monorepo for the desktop learning app, the FastAPI backend,
the public website, and the content/module packs used by the project.

## Current Versions

- Project release: `0.24.0`
- Desktop app line: `v23`
- Backend API metadata: `0.3.0`

## Repository Layout

- `minecraft_homework_overlay_v23.py` - current desktop app entry point
- `minecraft_coach/` - shared desktop package code
- `modules/` - installable learning modules
- `module_templates/` - starter templates for new modules
- `Electryk/` - bundled learning assets used by the app
- `coach_seed_v22.db` - seed database shipped with the app
- `server/` - FastAPI backend and backend docs
- `Site/` - static website assets
- `minecraft_homework_overlay_v*.py` - historical local snapshots kept in the repo

## What Gets Tracked

The repository is configured to keep source code, templates, docs, and required
bundled assets in Git, while ignoring:

- local runtime data in `coach_data/`
- local recordings
- generated build output in `build/`, `build_rebuild/`, `dist/`, and `dist_rebuild/`
- IDE metadata such as `.vs/`
- generated website bundles such as `Site/SiteUnzip/`

## Local Development

### Backend

```bash
pip install -r server/requirements.txt
uvicorn server.app.main:app --host 0.0.0.0 --port 8000
```

Useful local URLs:

- `http://localhost:8000/`
- `http://localhost:8000/health`

### Desktop App

The current desktop app entry point is:

```bash
python minecraft_homework_overlay_v23.py
```

## Git Branching Strategy

Use this branch model for GitHub:

- `main` - stable branch for tagged releases and production-ready changes
- `develop` - default integration branch for ongoing work
- `release/*` - optional stabilization branches before a public release
- `hotfix/*` - urgent fixes branched from `main`

Recommended flow:

1. Create feature branches from `develop`
2. Merge tested work into `develop`
3. Cut `release/*` when preparing a public version
4. Merge release candidates into `main`
5. Tag releases from `main`

## Versioning Rules

- Repository release tags should follow semantic versioning, current release: `v0.24.0`
- Desktop app snapshots can continue using the internal `v23`, `v24`, ... naming
- Backend API can evolve independently and currently reports `0.3.0`

## GitHub Automation

The repo includes a small GitHub Actions workflow that:

- installs backend dependencies
- compiles the active Python files
- verifies that the FastAPI app imports successfully

This keeps `main` and `develop` from drifting into a broken state after push.
