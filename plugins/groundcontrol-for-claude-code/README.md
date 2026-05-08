# groundcontrol-for-claude-code

A Claude Code plugin that turns your session into an autonomous coding agent against tasks in a GROUNDCONTROL workspace.

## Install

Once published in the AI Makers Lab marketplace:

```bash
/plugin marketplace add makerslab-ai/marketplace
/plugin install groundcontrol-for-claude-code@makerslab-ai
```

## Setup

Per project, one-time:

```
/gc-init
```

This asks for your GROUNDCONTROL API key (`gc_live_…` from Settings → API Keys at https://groundcontrol.makerslab.ai), optionally scopes the project to one initiative, writes `.env` and `.gitignore`, and verifies the connection.

## Run

```
/gc-loop
```

Starts a 15-minute loop. Every 15 minutes, the agent:

1. Checks for new comments on tasks assigned to you.
2. Picks the highest-priority `todo` (or resumes an `in_progress` task you started earlier).
3. Implements it — branches, commits, pushes.
4. Opens a PR against `main` via `gh`.
5. Posts a closing comment on the task with the PR URL, sets status to `done`.

Stop with `/loop stop`. One-off check: `/gc-check`.

## What's where

- Source: `claude-code-plugin/` in the [groundcontrol repo](https://github.com/cambuildr/groundcontrol).
- Built bundle: `plugins/groundcontrol-for-claude-code/server/dist/index.js` in the marketplace repo.
- Spec: `docs/superpowers/specs/2026-05-08-groundcontrol-for-claude-code-design.md` in the groundcontrol repo.

## Development

Source-of-truth lives in the groundcontrol repo. The marketplace repo only receives the built artifact.

```bash
cd claude-code-plugin/server
npm install
npm test
npm run build
```

To publish a release:

```bash
./claude-code-plugin/scripts/sync-to-marketplace.sh --patch
cd ~/repositories/marketplace
git add -A
git commit -m "release groundcontrol-for-claude-code v<version>"
git push
```

**Optional pre-commit hook:** Verify TS source changes still build before committing.

```bash
ln -sf ../../claude-code-plugin/scripts/pre-commit-check.sh .git/hooks/pre-commit
```
