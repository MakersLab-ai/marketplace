---
description: Verify the Cambuildr MCP connection and show what you can do next.
---

# /cambuildr:init

Check that the `cambuildr` connector is working and orient the user. This does
**not** set up the connector — for first-time setup (or to point it at a different
tenant), use `/cambuildr:connect`.

## Steps

1. **Check the `cambuildr` MCP server is connected.** If its tools aren't available,
   the connector hasn't been set up yet or isn't connected. Tell the user to run
   **`/cambuildr:connect`** to add it, and stop.

2. **Call `list-target-audiences`** with no arguments — a lightweight read that triggers
   the OAuth browser login on the first call. Tell the user "a browser tab may open for
   Cambuildr login" before you make the call.

3. **Read `cambuildr://tools`.** This resource lists the exact wire names of every tool,
   prompt and resource *this* tenant exposes, and it is authoritative — tool names are
   kebab-case (`list-content`, `instruct-assistant`, `set-workflow-graph`), and a tenant
   may have individual tools switched off at `/admin/settings/mcp`. Use it instead of
   assuming a name exists.

   Optionally read `cambuildr://tenant` too, for the tenant's name, public base URL,
   content languages and which MCP feature flags are in effect.

4. **Note what is missing, and why:**
   - Write tools absent → the `ai_mcp_write_access` feature flag is off.
   - `instruct-assistant` absent → the tenant has not opted in to the AI assistant.
     Only that tool disappears; every other tool still works. Say so plainly rather
     than reporting a broken connection.
   - A single named tool absent → it is toggled off at `/admin/settings/mcp`.

5. **Report back:**
   - Connectivity OK.
   - How many target audiences are visible (just the count is fine).
   - Any missing capability from step 4, with what enables it.
   - The discovery surfaces the tenant ships, so the user knows they exist:
     - **Prompts** — `build-landing-page-workflow`, `build-automated-mail-workflow`,
       `build-target-audience-workflow`, `build-workflow-automation`,
       `audit-tenant-content`. These carry the guided workflows server-side; prefer one
       when it matches the request.
     - **Resources** — `cambuildr://tools`, `cambuildr://tenant`,
       `cambuildr://trigger-actions`, and `cambuildr://workflows/{workflow_id}/building-blocks`.
   - A short menu of next steps:
     - "Create a landing page" → `/cambuildr:create-landing-page`
     - "Create a campaign or automated email" → `/cambuildr:create-mail`
     - "Build an automation" → `/cambuildr:create-workflow`
     - "See what already exists and what needs attention" → the `audit-tenant-content`
       prompt, or ask me to call `list-content`
     - "Look up a supporter" → ask me to call `read-person` or `list-people`

## If something fails

- **`list-target-audiences` returns a permission error** → the tool is disabled for this
  tenant. Tell the user to enable it at `/admin/settings/mcp` (or ask their Cambuildr
  account admin).
- **Tools still missing after `/cambuildr:connect`** → in Claude Code, restart so it
  re-reads the config; in a Claude app, re-open the connector in Settings and click
  **Connect**.
- **The feature flag is off** (`ai_mcp_server` missing) → a tenant-level Cambuildr
  setting the account admin must enable.
