---
description: Connect Claude Code to your Cambuildr tenant and verify the MCP setup.
---

# /cambuildr-init

Verify the Cambuildr MCP connection and trigger the OAuth login flow.

## Steps

1. **Check that the `cambuildr` MCP server is connected.** If it's not (e.g. tools are unavailable), report this back: the `CAMBUILDR_MCP_URL` env var is likely missing or wasn't picked up. Give the user this snippet and stop:

   ```bash
   # ~/.envrc (with direnv) or your shell rc
   export CAMBUILDR_MCP_URL="https://your-tenant.cambuildr.com/mcp"
   ```

   …and tell them to restart Claude Code so it re-reads `.mcp.json`.

2. **Call `ListTargetAudiences`** with no arguments. This is a lightweight read tool that will trigger the OAuth browser login on the very first call. Tell the user "a browser tab is about to open for Cambuildr login" before you make the call.

3. **Report back**:
   - Connectivity OK.
   - How many target audiences are visible (just the count is fine).
   - A short menu of next steps:
     - "Create a landing page" → `/cambuildr-create-landing-page`
     - "Create a campaign or automated email" → `/cambuildr-create-mail`
     - "List existing content" → ask me to call `ListContent`
     - "Look up a supporter" → ask me to call `ReadPerson` or `ListPeople`

## If something fails

- **`ListTargetAudiences` returns a permission error** → the tool is disabled for this tenant. Tell the user to enable it at `/admin/settings/mcp` (or ask their Cambuildr account admin).
- **The OAuth browser tab didn't open** → ask the user to fully restart Claude Code so it re-reads `.mcp.json`.
- **The feature flag is off** (`ai_mcp_server` missing) → tell the user this is a tenant-level Cambuildr setting and needs to be enabled by their account admin.
