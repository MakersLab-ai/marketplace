---
name: cambuildr
description: >
  Triggers when the user mentions Cambuildr, landing pages, campaign emails,
  triggered/automated emails, target audiences, supporters, donors, or asks to
  create/edit Cambuildr content. Use the cambuildr MCP tools. Two-step rule:
  every Create* tool returns an empty entity — always follow up with
  InstructAssistant to populate the body. Landing pages support signup forms,
  donations, countdowns, surveys, progress bars and teasers; emails support a
  much narrower set (text/image/button/POLL/share + merge tags).
version: 0.1.0
---

# Cambuildr

Cambuildr is a Laravel-based CRM for non-profits. The MCP server lets Claude Code read and manage your tenant's **people / supporters**, **target audiences (groups)**, **landing pages**, **campaign emails** (scheduled broadcasts), and **triggered emails** (event-driven automations).

## Critical rule — two-step content workflow

Every `Create*` MCP tool returns an entity with an **empty body**. The next step is **always** `InstructAssistant` with the matching `entity_type` and a natural-language instruction describing the content. Never tell the user "the landing page / email is done" before `InstructAssistant` has run.

| Step | Tool | Purpose |
|------|------|---------|
| 1 | `CreateLandingPage` / `CreateCampaignMail` / `CreateTrigger` | Scaffold the entity. Returns id + admin URL. Body is empty. |
| 2 | `InstructAssistant(entity_type, entity_id, instruction)` | Populate the body via natural language. **Mandatory.** |
| 3 (optional) | `Update*` | Bind audiences/tags, set delay, publish, activate trigger. |

Use `Update*` only for **entity metadata** (name, description, audiences, publish state, trigger active flag, delay). Use `InstructAssistant` for **everything inside the body**, including the email subject and preheader.

## Tool reference (17 tools)

### Read

| Tool | Purpose |
|------|---------|
| `ListContent` | List landing pages / campaign mails / triggers / pages. Optional `type` filter and `search`. Paginated. |
| `ListPeople` | Paginated people search. Filter by `target_audience_id` and `search` (name/email). |
| `ListTargetAudiences` | List non-archived target audiences with name, description, people count. |
| `GetLandingPage` | Full landing-page details (variants, slug, publish state, share metadata, tags). |
| `GetCampaignMail` | Full campaign-mail details (state, planned date, variants, audiences, tags, metrics). |
| `GetTrigger` | Full triggered-mail details (action binding, active state, delay config, variants). |
| `GetTargetAudience` | Target-audience details (people count, computation state, archive status). |
| `ReadPerson` | Person record (name, email, tags, addresses, donation summary). |

### Write — entity scaffolding

| Tool | What's possible | What's NOT possible |
|------|------------------|----------------------|
| `CreateLandingPage` | Create empty landing page: `name`, `description`, `page_title`. Returns id + admin URL. | Does not set body, share metadata, or publish state. Body → `InstructAssistant`. Metadata → `UpdateLandingPage`. |
| `UpdateLandingPage` | Update `name`, `description`, `page_title`, `share_title`, `share_description`, `is_published`. | Cannot edit body — that's `InstructAssistant`. Cannot manage variants or tags directly. |
| `CreateCampaignMail` | Create campaign mail in `EDITING` state: `name`, `description`. Returns id + admin URL. | Does not set subject/preheader/audience/planned date/body. Subject + preheader + body → `InstructAssistant`. Audience + tags → `UpdateCampaignMail`. |
| `UpdateCampaignMail` | Update `name`, `description`, `group_ids` (target audiences), `tag_ids`. Only while in `EDITING` state. | Cannot advance state — user does that in the admin UI. Cannot set planned date. Cannot edit body. |
| `CreateTrigger` | Create triggered mail (inactive by default): `name`, `description`, optional `action_name` + `action_context`. Returns id + admin URL. | Body empty → `InstructAssistant`. Stays inactive until `UpdateTrigger active=true`. |
| `UpdateTrigger` | Update `name`, `description`, `active` flag, `delay` + `delay_days` + `delay_time HH:MM`. | Cannot edit body. Cannot change action binding after creation. Subject/preheader → `InstructAssistant`. |
| `CreateTargetAudience` | Create empty target audience: `name`, `description`. | Cannot define filter rules — those are admin-UI-only. |
| `UpdateTargetAudience` | Update `name`, `description`. | Cannot modify filter rules or archive state. |

### AI content

`InstructAssistant(entity_type, entity_id, variant_id?, instruction)` — natural-language edit of the BeeFree content body. `entity_type` is one of `landing_page` / `campaign_mail` / `trigger`. `instruction` is up to 10,000 characters. If `variant_id` is omitted, the first variant is used.

Internally `InstructAssistant` dispatches to one of two specialised agents:
- `full-landing-page` → for `entity_type=landing_page`
- `full-email` → for `entity_type=campaign_mail` **and** `entity_type=trigger`

The two agents have very different capability surfaces — see the matrix below.

## Capability matrix — what each `entity_type` can build

### Standard BeeFree blocks (available in all three)

Text, Paragraph, Heading, Button, Image, Video, Spacer, Divider, Icons, Social, List, Menu, raw HTML.

Rows and columns with mobile-responsive overrides: `style` (desktop), `mobileStyle` (mobile-only), `computedStyle.hideContentOnMobile` / `hideContentOnDesktop` / `rowColStackOnMobile` / `rowReverseColStackOnMobile`.

### Custom blocks — availability per entity type

| Block | `landing_page` | `campaign_mail` | `trigger` | Notes |
|-------|:--------------:|:---------------:|:---------:|-------|
| **Countdown timer** (target date + headline) | ✅ | ❌ | ❌ | Landing-page-only. |
| **Signup form** — multi-field (core: email/firstname/lastname/phone/address/zip/city/state/country; or custom field / tag); field types TEXT, MULTISELECT, CHECKBOX, DROPDOWN, TEXTAREA, DATE, RADIO, UPLOAD; multi-step pages; opt-in / GDPR disclaimer | ✅ | ❌ | ❌ | Landing-page-only. |
| **Donation block** — 3 preset amounts, anonymous donations, address gating, tax-deduction text, webhook code, thank-you screen | ✅ | ❌ | ❌ | Landing-page-only. |
| **Purchase block** — Stripe; product title/description/image/price/currency, address gating | ✅ | ❌ | ❌ | Landing-page-only. |
| **Survey — POLL** (multiple-choice, 2–4 answers) | ✅ | ✅ | ✅ | Only POLL works in emails. |
| **Survey — SENTIMENT** (emoji scale 0–10) | ✅ | ❌ | ❌ | Landing-page-only. |
| **Survey — MULTI_SWIPE** (swipe through questions) | ✅ | ❌ | ❌ | Landing-page-only. |
| **Survey — VERIFIED_VOTING** (email/SMS verified) | ✅ | ❌ | ❌ | Landing-page-only. |
| **Share block** — mail / Facebook / X-Twitter / LinkedIn / WhatsApp / Telegram / Threads / Bluesky | ✅ (URL defaults to page) | ✅ (URL required) | ✅ (URL required) | |
| **Progress bar** — source: SIGNUPS / DONATIONS / GROUP; objective + minimum; postfix label | ✅ | ❌ | ❌ | Landing-page-only. |
| **Event teaser** (preview or wall, filter by category) | ✅ | ❌ | ❌ | Needs existing Event Page ID. |
| **Commitment teaser** (pledges/signatures wall; card / list / simple layout) | ✅ | ❌ | ❌ | Needs existing Commitment Page ID. |
| **UGC voting / UGC teaser** | ✅ | ❌ | ❌ | Needs existing UGC Page ID. |

### Entity-type-specific knobs (also edited via `InstructAssistant`)

| Knob | landing_page | campaign_mail | trigger |
|------|:---:|:---:|:---:|
| Page title (browser tab) | ✅ | ❌ | ❌ |
| Share title / share description (social previews) | ✅ | ❌ | ❌ |
| URL slug / page language | ✅ | ❌ | ❌ |
| Email subject (max 998 chars) | ❌ | ✅ | ✅ |
| Email preheader (inbox preview) | ❌ | ✅ | ✅ |

### Personalisation / merge tags (emails only)

- Syntax: `{{ var:placeholder_name }}`.
- Available everywhere in emails (headings, paragraphs, buttons, links).
- **Campaign mail**: person fields (firstname, lastname, email), customer fields, custom fields.
- **Trigger**: same as campaign mail **plus** action-specific placeholders from the trigger's `action_name` / `action_context` (e.g. donation amount on `donated`, event data on event triggers). The assistant introspects the available list at runtime via `GetAvailablePlaceholders`.
- Internal links in emails are auto-prefixed with `{{ var:customer:url }}` by the agent.
- **Landing pages do not have merge tags.**

### Styling rules (both agents enforce)

- Colors: hex only (`#ffffff`, `#0B1020`); 8-digit hex for opacity (`#ffffff1a`); `transparent` / `inherit` allowed. **No rgba/rgb/hsl.**
- Pixel values only (`40px`).
- Rows must declare `background-color`, `background-image: "none"`, `background-repeat: "no-repeat"`, `background-position: "top left"`.

### Templates (both agents)

The agent can pull design tokens (fonts, colors, button styles, spacing) from existing landing pages or emails in the same tenant via `ListAvailableTemplates` + `ExtractStyleFromTemplate`. Cross-entity reuse is supported.

## Campaign mail vs triggered mail

| | Campaign mail | Triggered mail |
|---|---|---|
| Admin UI label | **Campaign Emails** | **Automated Emails** |
| Trigger | Scheduled date | Event (action_name + action_context) |
| State machine | `EDITING → READY → RUNNING → SENT` | `active: false / true` |
| A/B testing | Yes (`test_duration`, `test_percent`, `winning_selection`) | No |
| Delay | n/a | Optional (`delay_days` + `delay_time HH:MM`) |
| Activation | User advances state in admin UI | `UpdateTrigger active=true` |
| Typical use | Newsletters, announcements, one-off blasts | Signup confirmations, donation thank-yous, birthday greetings, drip steps |
| User-speak that maps here | "send a newsletter on Friday", "blast the supporters about X", "schedule an email" | "thank donors automatically", "welcome new signups", "birthday email", "auto-confirm" |

### Common trigger `action_name` values
`signed_up`, `donated`, `accepted-optin`, `recruited`, `clicked`, `has-birthday`. (There are more — ask the user or list via Cambuildr docs if needed.)

### Common trigger `action_context` values
`campaign`, `landing_page`.

## Patterns

- **Before writing, list — before editing, get.** Run `ListContent` / `ListTargetAudiences` first when context is needed; `Get*` to inspect an existing entity; `Update*` only after `Get*` confirms the state.
- **`InstructAssistant` for body, `Update*` for metadata.** Audience binding, publish flag, trigger delay, trigger `active` — all `Update*`. Body content, subject, preheader, layout, styling — all `InstructAssistant`.
- **Refuse landing-page-only blocks inside an email.** If a user asks for a donation block, signup form, countdown, multi-type survey, progress bar, or teaser **inside an email**, stop and explain. Suggest creating a landing page with that block and linking to it from the email.
- **Respect tenant tool gating.** If a tool returns a permission error, the tenant disabled it in `/admin/settings/mcp`. Tell the user; don't retry.
- **Triggers stay inactive until you flip them.** Only call `UpdateTrigger active=true` after the body looks right.
- **Campaign mails stay in `EDITING`.** Don't promise the email will send — the user advances to `READY` in the admin UI.
- **Don't paste huge HTML.** Always go through `InstructAssistant` with a natural-language brief; the agent builds the BeeFree JSON correctly with valid styling rules.
- **Re-edit by id.** To iterate on a body, call `InstructAssistant` again with the same `entity_id` and a follow-up instruction ("make the headline bolder", "add a second CTA below the donation block").
