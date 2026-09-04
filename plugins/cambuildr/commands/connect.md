---
description: Connect Claude to your Cambuildr tenant — auto-adds the MCP connector in Claude Code, or guides you through adding it in the Claude apps.
---

# /cambuildr:connect

Set up the `cambuildr` MCP connector for the user's tenant, then verify it.

Cambuildr is multi-tenant: every account has its own endpoint at
`https://<tenant>.cambuildr.com/mcp` (or a custom domain). This command wires that
endpoint up as an MCP server named **`cambuildr`** — the exact name the skill and
the other `/cambuildr:*` commands expect. Don't rename it.

## Step 0 — Offer the tenant install path first

If the user has admin access to their Cambuildr tenant, the shortest route is not this
command at all. Their admin offers a ready-made install line at **`/admin/settings/mcp`**:

```
/plugin marketplace add https://<tenant>.cambuildr.com/mcp-plugin/<token>/marketplace.json
```

That archive ships the plugin with their `/mcp` URL already baked in, so no connector has
to be added by hand. It needs **Claude Code 2.1.224 or newer** (the `archive` marketplace
source type). Mention it once; if the user cannot reach that settings page, is on an older
Claude Code, or is in a Claude app rather than the CLI, continue with this command.

## Step 1 — Get the tenant endpoint

Ask the user for their Cambuildr tenant if you don't already have it. Accept any of:

- a bare slug — `acme` → `https://acme.cambuildr.com/mcp`
- a host — `acme.cambuildr.com` → `https://acme.cambuildr.com/mcp`
- a full URL — `https://acme.cambuildr.com` → append `/mcp`
- a custom domain — use exactly what they give, just ensure it ends in `/mcp`

Normalize to a single `https://…/mcp` URL (call it `<URL>`) and confirm it back to
the user before continuing.

## Step 2 — Add the connector

**First, check whether it already exists.** If a `cambuildr` MCP server is already
connected (its tools are available to you), skip to Step 3. If one exists but points
at the wrong tenant, remove it first (see below) and re-add.

**If you can run shell commands (you're in Claude Code):**

Confirm the CLI is present, then add the server user-wide:

```bash
command -v claude && claude mcp add --transport http cambuildr "<URL>" --scope user
```

- `--scope user` makes the connector available in every project. Use `--scope local`
  instead if the user wants it only in the current project.
- To fix a wrong URL, remove the old one first: `claude mcp remove cambuildr`
  (add `--scope local`/`--scope user` to match how it was added), then re-add.
- The tools may load right away; if they don't appear, tell the user to restart
  Claude Code so it re-reads the MCP config.

**If you cannot run shell commands (you're in a Claude app — Cowork, Desktop, or web):**

You can't create the connector automatically here — connectors are added in Settings
by design, and there's no tool to do it from the conversation. Give the user these
exact, personalized steps:

1. Open **Settings → Connectors** and click **Add custom connector**.
2. **Name:** `cambuildr` (use this exact name so the `/cambuildr:*` commands find it).
3. **Remote MCP server URL:** `<URL>`
4. Leave OAuth Client ID / Secret blank — Cambuildr uses OAuth 2.1 discovery.
5. Save, then click **Connect** and log in when the browser prompts.

Then wait for the user to confirm they've added and connected it before continuing.

## Step 3 — Verify

Tell the user "a browser tab may open for Cambuildr login," then call
`list-target-audiences` with no arguments — a lightweight read that triggers the OAuth
login on the first call.

Then check what the tenant actually exposes: read the `cambuildr://tools` resource, or
look at which tools are registered. Note two things for the report:

- whether the write tools are present (they need the `ai_mcp_write_access` feature flag);
- whether `instruct-assistant` is present (it needs the tenant's AI opt-in, and its absence
  disables only that tool — everything else still works).

Report back:

- Connectivity OK.
- How many target audiences are visible (count is enough).
- Any capability that is missing, stated plainly, with what enables it.
- A short next-steps menu:
  - "Create a landing page" → `/cambuildr:create-landing-page`
  - "Create a campaign or automated email" → `/cambuildr:create-mail`
  - "Build an automation" → `/cambuildr:create-workflow`
  - "See what already exists" → the `audit-tenant-content` prompt, or ask me to call `list-content`
  - "Look up a supporter" → ask me to call `read-person` or `list-people`

## If something fails

- **`list-target-audiences` returns a permission error** → the tool is disabled for this
  tenant. Tell the user to enable it at `/admin/settings/mcp` (or ask their Cambuildr
  account admin).
- **No browser tab opened / tools still missing** → in Claude Code, restart so it
  re-reads the config; in a Claude app, re-open the connector in Settings and click
  **Connect**.
- **The feature flag is off** (`ai_mcp_server` missing) → a tenant-level Cambuildr
  setting; the account admin must enable it.
- **Only read tools appear** → `ai_mcp_write_access` is off for the tenant.
- **`instruct-assistant` is absent** → the tenant has not opted in to the AI assistant.
  Not a connection fault; say so and carry on with the other tools.
- **Wrong tenant URL** → re-run this command; remove the bad server first
  (`claude mcp remove cambuildr` in Claude Code, or delete the connector in Settings).
