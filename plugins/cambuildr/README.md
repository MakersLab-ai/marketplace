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

### MCP server: `cambuildr` (remote HTTP)
Talks to your tenant's `/mcp` endpoint over HTTP. **Authentication:** OAuth 2.1 (RFC 8414 discovery). On first MCP call Claude Code opens your browser, you log into Cambuildr, and you're connected — no API key in config.

### Skill: `cambuildr`
Teaches Claude the two-step create-then-`InstructAssistant` workflow, the capability matrix per entity type, and when to pick campaign vs triggered.

### Commands
- `/cambuildr-init` — verify env + trigger OAuth login.
- `/cambuildr-create-landing-page [name]` — scaffold a landing page and populate it.
- `/cambuildr-create-mail [campaign|triggered] [name]` — scaffold an email and populate it.

## Installation

```
/plugin marketplace add makerslab-ai/marketplace
/plugin install cambuildr@makerslab-ai
```

## Setup

1. **Find your tenant URL.** It's your Cambuildr admin URL with `/mcp` appended, e.g. `https://your-tenant.cambuildr.com/mcp`.
2. **Export it as `CAMBUILDR_MCP_URL`.** [direnv](https://direnv.net/) is recommended so the variable is scoped to the project:
   ```bash
   # .envrc
   export CAMBUILDR_MCP_URL="https://your-tenant.cambuildr.com/mcp"
   ```
   Or add it to your shell rc (`~/.bashrc` / `~/.zshrc`).
3. **Restart Claude Code** so it picks up the new env var.
4. **Run `/cambuildr-init`.** Your browser opens the Cambuildr login page; after you log in, the MCP connects and the command reports tenant connectivity.

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
- **Triggers stay inactive** until you call `UpdateTrigger` with `active=true`. The `/cambuildr-create-mail triggered` command does this for you after the body is populated.

## Troubleshooting

- **"`CAMBUILDR_MCP_URL` not set."** Export the env var (see Setup) and restart Claude Code.
- **No browser opened on first MCP call.** Restart Claude Code so it re-reads `.mcp.json`.
- **"Tool not enabled for this tenant."** Your Cambuildr admin needs to toggle the tool on at `/admin/settings/mcp`.
- **"Feature `ai_mcp_server` not available."** The feature flag must be turned on for your tenant.
- **My trigger isn't firing.** Check `GetTrigger` returns `active: true`. If not, `UpdateTrigger` with `active=true` after populating the body.
