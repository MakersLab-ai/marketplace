<!--
  GENERATED — do not edit here.

  The source of truth for this plugin is resources/mcp-plugin/ in the private
  MakersLab-ai/cambuildr repository, so it changes in the same pull request as
  the MCP server it documents and cannot drift from it. A release job in that
  repository publishes this copy; edits made here are overwritten.
-->

# Cambuildr Plugin

Manage your [Cambuildr](https://cambuildr.com/) tenant — landing pages, campaign emails, automated (triggered) emails, workflows, target audiences, tags, the media library and supporters — directly from Claude.

## What this plugin does

- **Read**: list and inspect landing pages, campaign mails, triggered mails, workflows, target audiences, tags, custom fields, media library items and people records.
- **Write**: create and update landing pages, campaign mails, triggered mails, target audiences and workflows. Bind trigger actions. Set workflow start conditions and graphs. Author externally hosted HTML landing pages and their signup forms. Add media library items.
- **AI content**: fill the body of a landing page or email, the rules of a target audience, or the graph of a workflow with natural-language instructions via `instruct-assistant`. The commands always follow a `create-*` call with `instruct-assistant`, so you never end up with an empty entity.

Three things in Cambuildr are easy to confuse:

- **Campaign mail** ("Campaign Emails" in the admin UI) — a scheduled broadcast to a target audience.
- **Triggered mail** ("Automated Emails") — one email sent when one bound event fires, with an optional delay.
- **Workflow** ("Automations") — a multi-step graph: send, tag, wait, branch, call a webhook.

## Tool names are kebab-case

The server derives every tool name from its class name in kebab-case: `list-target-audiences`, `instruct-assistant`, `set-workflow-graph`. There are no PascalCase names. Read the `cambuildr://tools` resource when you are unsure — it is authoritative for the tenant you are connected to.

The server exposes **34 tools, 5 prompts and 4 resources**.

## Installation

```
/plugin marketplace add makerslab-ai/marketplace
/plugin install cambuildr@makerslab-ai
/cambuildr:connect
```

`/cambuildr:connect` asks for your tenant and wires up the connector — a slug (`acme`), a host, or a full URL all work. Your Cambuildr admin also shows the exact MCP server URL and per-client setup steps at **`/admin/settings/mcp`**, if you would rather add the connection by hand in your client's own settings.

### Updates

Both paths update through `/plugin marketplace update` then `/plugin update`. Not a silent auto-update: the catalog is re-read only when you ask.

### Claude Desktop (`.mcpb`)

Out of scope. The `.mcpb` bundle format is stdio-only and cannot express a remote OAuth-authenticated HTTP server, which is what the Cambuildr MCP endpoint is. Use Claude Code, or add the connector by hand in a Claude app as `/cambuildr:connect` describes.

## Components

### MCP connector: `cambuildr` (remote HTTP)

Talks to your tenant's `/mcp` endpoint over HTTP. The plugin carries no connector of its own — one fixed URL cannot serve every tenant — so `/cambuildr:connect` adds it for you. **Authentication:** OAuth 2.1 (RFC 8414 discovery). On the first tool call your browser opens, you log into Cambuildr, and you are connected — no API key in any config file.

The server must be named exactly `cambuildr`; the skill and the commands address it by that name.

### Skill: `cambuildr`

The accurate tool reference, the create-then-`instruct-assistant` rule, the capability matrix per entity type, the trigger-action binding sequence, workflows, hosted pages and the media library.

### Commands

- `/cambuildr:connect` — add the connector for your tenant (automatic in Claude Code, guided in the Claude apps) and verify it.
- `/cambuildr:init` — verify an existing connection and show what you can do next.
- `/cambuildr:create-landing-page [name]` — scaffold a landing page and populate it.
- `/cambuildr:create-mail [campaign|triggered] [name]` — scaffold an email and populate it.
- `/cambuildr:create-workflow [name]` — scaffold an automation, set its start condition and graph, then activate it.

### Server-side prompts

The same guided workflows also ship on the server as MCP prompts, so they reach any MCP client, not only ones that can install this plugin. Prefer them when one matches the request:

`build-landing-page-workflow`, `build-automated-mail-workflow`, `build-target-audience-workflow`, `build-workflow-automation`, `audit-tenant-content`.

### Server-side resources

| Resource | URI |
|---|---|
| Tool catalog (authoritative wire names) | `cambuildr://tools` |
| Tenant profile (flags, languages, base URL) | `cambuildr://tenant` |
| Trigger action catalog | `cambuildr://trigger-actions` |
| Workflow building blocks | `cambuildr://workflows/{workflow_id}/building-blocks` |

## Tenant prerequisites

| Requirement | Gates |
|---|---|
| Feature flag `ai_mcp_server` | The MCP server itself. Without it there is no endpoint. |
| Feature flag `ai_mcp_write_access` | Every write tool. Without it only the read tools are registered. |
| AI opt-in for the customer | `instruct-assistant` only. Without it that one tool is **absent** while everything else works. |
| Per-tool toggles at `/admin/settings/mcp` | Individual tools. A disabled tool is not registered. |

`instruct-assistant` also needs AI credit; an exhausted balance returns an error asking for a top-up.

If you do not have access to those settings, ask your Cambuildr account admin.

## Capability matrix

`instruct-assistant` builds different blocks depending on the entity type:

| Block | Landing page | Campaign mail | Triggered mail |
|---|:---:|:---:|:---:|
| Text, headings, images, buttons, video, dividers, lists, menus, HTML | Yes | Yes | Yes |
| Signup form (multi-field, opt-in, multi-step) | Yes | No | No |
| Donation block (preset amounts, anonymous, tax-deduction) | Yes | No | No |
| Purchase block (Stripe) | Yes | No | No |
| Countdown timer | Yes | No | No |
| Survey — POLL (multiple choice) | Yes | Yes | Yes |
| Survey — SENTIMENT / MULTI_SWIPE / VERIFIED_VOTING | Yes | No | No |
| Progress bar (signups / donations / group) | Yes | No | No |
| Event / Commitment / UGC teasers | Yes | No | No |
| Share buttons (mail, Facebook, X, LinkedIn, WhatsApp, Telegram, Threads, Bluesky) | Yes | Yes | Yes |
| Merge tags `{{ var:firstname }}`, custom fields, action placeholders | No | Yes | Yes (plus action context) |

Ask for a landing-page-only block inside an email and the skill will steer you to put it on a landing page and link to it from the email.

Two entity types have no blocks at all: a **target audience** is filter rules, and a **workflow** is a node graph. `instruct-assistant` writes both from natural language.

## Workflow notes

- **Two-step creation.** Every `create-*` tool returns an empty entity. The commands follow up with `instruct-assistant`. If you call the tools directly, do the same.
- **Bind triggers to internal actions.** `create-trigger` takes a name; `list-trigger-actions` gives the dotted `name.context` keys (`signed-up.campaign`, `donated.donation`, `has-birthday.database`); `set-trigger-action` binds one. A free-text action name requires an explicit `is_internal_action: false` and means an external webhook that no internal Cambuildr event fires.
- **Target audiences start empty.** `create-target-audience` returns a group matching nobody. The `instruct-assistant` follow-up that writes its rules is mandatory, not optional.
- **Triggered mails resolve their variant.** `instruct-assistant` no longer needs an explicit `variant_id`; the first variant is used.
- **Workflow graphs are full replaces.** `set-workflow-graph` takes the complete node and edge lists every time. Read the current graph with `get-workflow` and edit that.
- **A delete-person workflow cannot be self-activated.** `update-workflow active=true` on a graph containing a `delete_person` action returns a refusal saying review was requested; only Cambuildr can switch it on.
- **Campaign mail state.** New campaign mails sit in `EDITING`. Advancing to `READY`, which schedules the send, is a manual step in the admin UI.
- **Triggers and workflows stay inactive** until you flip `active=true`, which the commands do after the content is populated.
- **Hosted landing pages are experimental.** They are raw-HTML pages with no editor, and none of the custom blocks apply to them. Call `get-hosted-landing-page-contract` before authoring one.

## Troubleshooting

- **No `cambuildr` tools at all.** The connector is not set up — run `/cambuildr:connect`, or install through your tenant's own marketplace URL.
- **`/plugin marketplace add` fails on the tenant URL.** Your Claude Code is older than 2.1.224 and does not know the `archive` source type. Upgrade, or use the public marketplace plus `/cambuildr:connect`.
- **`instruct-assistant` is missing but everything else works.** The tenant has not opted in to the AI assistant. That is a tenant setting, not a connection fault, and it removes only that one tool. Ask your Cambuildr account admin to opt in, or do the content work in the admin UI.
- **"AI credits exhausted."** Top up the tenant's AI credit balance. Retrying does not help.
- **Only read tools are present.** The `ai_mcp_write_access` feature flag is off for your tenant.
- **One specific tool is missing.** It is toggled off at `/admin/settings/mcp`.
- **"Feature `ai_mcp_server` not available."** The feature flag must be enabled for the tenant.
- **Connected to the wrong tenant.** Re-run `/cambuildr:connect`; in Claude Code remove the old server first with `claude mcp remove cambuildr`, in a Claude app delete the connector in Settings.
- **No browser opened on the first tool call.** In Claude Code, restart so it re-reads the MCP config; in a Claude app, re-open the connector in Settings and click **Connect**.
- **My trigger is not firing.** Check `get-trigger`. It needs both `active: true` **and** an internal action binding. A trigger whose action came from free text is an external webhook binding and no Cambuildr event will fire it — rebind it with `set-trigger-action`.
- **My target audience matches nobody.** It was created without rules. Run `instruct-assistant` with `entity_type: target_audience`, then re-read the count with `get-target-audience`.
- **My workflow does nothing.** It needs a start condition (`set-workflow-start-condition`), a published graph (`set-workflow-graph`), and `active=true`.
- **A tool name is rejected.** Names are kebab-case. Read `cambuildr://tools` for the exact spellings.
