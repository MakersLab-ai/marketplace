# Cambuildr Plugin

Manage your [Cambuildr](https://cambuildr.com/) tenant — landing pages, campaign emails, automated (triggered) emails, target audiences, and supporters — directly from Claude Code.

## What this plugin does

- **Read**: list and inspect landing pages, campaign mails, triggered mails, target audiences, and people records.
- **Write**: create and update landing pages, campaign mails, triggered mails, and target audiences. Bind audiences and tags. Toggle triggers active/inactive. Configure trigger delays.
- **AI content**: fill the body of any landing page, campaign mail, or triggered mail with natural-language instructions via `InstructAssistant`. The plugin's commands always follow `Create*` with `InstructAssistant` so you never end up with an empty entity.

Campaign emails and triggered emails are different things in Cambuildr:

- **Campaign mail** ("Campaign Emails" in the admin UI) — a scheduled broadcast to a target audience.
- **Triggered mail** ("Automated Emails" in the admin UI) — an event-driven automation, bound to an action (signup, donation, birthday, …) with optional delay.

## Components

### MCP connector: `cambuildr` (remote HTTP)
Talks to your tenant's `/mcp` endpoint over HTTP. Because each tenant has its own URL, the connector is **not bundled** — you add it once with `/cambuildr:connect` (see Setup), which auto-configures it in Claude Code and guides you through it in the Claude apps (Cowork / Desktop / web). **Authentication:** OAuth 2.1 (RFC 8414 discovery). On the first tool call your browser opens, you log into Cambuildr, and you're connected — no API key in config.

### Skill: `cambuildr`
Teaches Claude the two-step create-then-`InstructAssistant` workflow, the capability matrix per entity type, and when to pick campaign vs triggered.

### Commands
- `/cambuildr:connect` — add the connector for your tenant (auto in Claude Code, guided in the apps) and verify it.
- `/cambuildr:init` — verify an existing connection and show next steps.
- `/cambuildr:create-landing-page [name]` — scaffold a landing page and populate it.
- `/cambuildr:create-mail [campaign|triggered] [name]` — scaffold an email and populate it.

## Installation

```
/plugin marketplace add makerslab-ai/marketplace
/plugin install cambuildr@makerslab-ai
```

Then run `/cambuildr:connect` to add the connector for your tenant.

## Setup

Run **`/cambuildr:connect`** and give it your tenant when asked — a bare slug (`acme`), a host (`acme.cambuildr.com`), or a full URL all work; it normalizes to `https://<tenant>.cambuildr.com/mcp`. What happens next depends on where you're running:

- **Claude Code (CLI):** the command adds the connector for you (`claude mcp add --transport http cambuildr <url> --scope user`) and verifies it. No env vars, no restart dance.
- **Claude apps (Cowork / Desktop / web):** connectors can only be added in Settings, so the command hands you the exact steps and your ready-to-paste URL — **Settings → Connectors → Add custom connector**, name it `cambuildr`, paste the URL, leave OAuth fields blank, then **Connect**.

Either way, on the first tool call your browser opens the Cambuildr login; after you log in you're connected. Later, `/cambuildr:init` just re-verifies and shows what you can do next.

> **Why not bundled?** Every Cambuildr tenant has its own URL, and a plugin-bundled remote connector installs with one fixed URL and no way to edit it in the apps. Adding it per-tenant via `/cambuildr:connect` is what makes the plugin work in Cowork/Desktop, not just the CLI.

## Tenant prerequisites

Your Cambuildr account must have:

- Feature flag `ai_mcp_server` enabled.
- The MCP tools you want to use toggled on in `/admin/settings/mcp`.

If you don't have access to those settings, ask your Cambuildr account admin.

## What you can build

The AI content tool (`InstructAssistant`) supports different blocks depending on the entity type:

| Block | Landing page | Campaign mail | Triggered mail |
|---|:---:|:---:|:---:|
| Text, headings, images, buttons, video, dividers, lists, menus, HTML | ✅ | ✅ | ✅ |
| **Signup form** (multi-field, opt-in, multi-step) | ✅ | ❌ | ❌ |
| **Donation block** (preset amounts, anonymous, tax-deduction) | ✅ | ❌ | ❌ |
| **Purchase block** (Stripe) | ✅ | ❌ | ❌ |
| **Countdown timer** | ✅ | ❌ | ❌ |
| **Survey — POLL** (multiple-choice) | ✅ | ✅ | ✅ |
| **Survey — SENTIMENT / MULTI_SWIPE / VERIFIED_VOTING** | ✅ | ❌ | ❌ |
| **Progress bar** (signups / donations / group) | ✅ | ❌ | ❌ |
| **Event / Commitment / UGC teasers** | ✅ | ❌ | ❌ |
| **Share buttons** (FB, X, LinkedIn, WhatsApp, Telegram, Threads, Bluesky, mail) | ✅ | ✅ | ✅ |
| **Merge tags** `{{ var:firstname }}`, custom fields, action-specific placeholders | ❌ | ✅ | ✅ (+ action context) |

If you ask for a landing-page-only block inside an email, the skill will steer you to put it on a landing page and link to it from the email.

## Workflow notes

- **Two-step creation.** Every `Create*` MCP tool returns an empty entity. The plugin's commands always follow up with `InstructAssistant` to fill the body. If you call the MCP tools directly, do the same.
- **Campaign mail state.** New campaign mails sit in `EDITING`. Advancing to `READY` (which schedules the send) is a manual step in the Cambuildr admin UI.
- **Triggers stay inactive** until you call `UpdateTrigger` with `active=true`. The `/cambuildr:create-mail triggered` command does this for you after the body is populated.

## Troubleshooting

- **`cambuildr` tools aren't available.** The connector isn't set up yet — run `/cambuildr:connect`.
- **Connected to the wrong tenant.** Re-run `/cambuildr:connect`; in Claude Code remove the old server first with `claude mcp remove cambuildr`, in the apps delete the connector in Settings.
- **No browser opened on first tool call.** In Claude Code, restart so it re-reads the MCP config; in a Claude app, re-open the connector in Settings and click **Connect**.
- **"Tool not enabled for this tenant."** Your Cambuildr admin needs to toggle the tool on at `/admin/settings/mcp`.
- **"Feature `ai_mcp_server` not available."** The feature flag must be turned on for your tenant.
- **My trigger isn't firing.** Check `GetTrigger` returns `active: true`. If not, `UpdateTrigger` with `active=true` after populating the body.
