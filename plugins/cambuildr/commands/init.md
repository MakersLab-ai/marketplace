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

2. **Call `ListTargetAudiences`** with no arguments — a lightweight read that triggers
   the OAuth browser login on the first call. Tell the user "a browser tab may open for
   Cambuildr login" before you make the call.

3. **Report back:**
   - Connectivity OK.
   - How many target audiences are visible (just the count is fine).
   - A short menu of next steps:
     - "Create a landing page" → `/cambuildr:create-landing-page`
     - "Create a campaign or automated email" → `/cambuildr:create-mail`
     - "List existing content" → ask me to call `ListContent`
     - "Look up a supporter" → ask me to call `ReadPerson` or `ListPeople`

## If something fails

- **`ListTargetAudiences` returns a permission error** → the tool is disabled for this
  tenant. Tell the user to enable it at `/admin/settings/mcp` (or ask their Cambuildr
  account admin).
- **Tools still missing after `/cambuildr:connect`** → in Claude Code, restart so it
  re-reads the config; in a Claude app, re-open the connector in Settings and click
  **Connect**.
- **The feature flag is off** (`ai_mcp_server` missing) → a tenant-level Cambuildr
  setting the account admin must enable.
