---
description: One-time setup for GROUNDCONTROL in this project. Writes .env and verifies the API key.
---

# /gc-init

Run this once per project. It collects the GROUNDCONTROL API key and optional initiative ID, writes them to `.env`, ensures `.env` and `.gc-state.json` are gitignored, and verifies the connection.

## Steps

1. **Ask the user for the API key.** It must start with `gc_live_`. If they don't have one, instruct them to register at https://groundcontrol.makerslab.ai and create one in Settings → API Keys.

2. **Validate format.** If the pasted key does not start with `gc_live_`, ask them to re-paste — it may have been trimmed.

3. **Ask if they want to scope this project to one initiative.** If yes, ask for the initiative UUID (visible in the URL when viewing the initiative in the GROUNDCONTROL UI). Optional — they can skip.

4. **Write `.env`** at the project root. If the file already exists, only update / add `GC_*` lines, do not touch other entries:
   ```
   GC_API_KEY=gc_live_...
   GC_API_URL=https://groundcontrol.makerslab.ai/api/v1
   GC_INITIATIVE_ID=<uuid-or-empty>
   ```

5. **Update `.gitignore`.** Both `.env` and `.gc-state.json` must be present. If `.gitignore` doesn't exist, create it with both entries. If it exists, append any missing ones (do not duplicate).

6. **Verify the connection** by calling the MCP tool `gc_get_context`. The MCP server re-reads `.env` from the project root on every tool call, so the freshly written credentials take effect immediately — no Claude Code restart or `/mcp` reconnect is required. If the call fails:
   - 401 / "API key validation failed": ask the user to regenerate the key and try again.
   - Network error: surface the error and stop.

7. **On success**, print:
   ```
   GROUNDCONTROL connected as <user.name>.
   Workspace: <tenant.name>
   Next: run /gc-loop to start the 15-minute task loop, or /gc-check for a single iteration.
   ```

## Failure modes

- Key doesn't start with `gc_live_` → ask for re-paste.
- `.gitignore` write failure → fail loudly, do NOT proceed (refusing to leave the key without gitignore protection).
- `gc_get_context` 401 → ask to regenerate the key in workspace settings.
