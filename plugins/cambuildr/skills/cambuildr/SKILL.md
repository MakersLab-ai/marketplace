---
name: cambuildr
description: >
  Triggers when the user mentions Cambuildr, landing pages, campaign emails,
  triggered/automated emails, workflows/automations, target audiences,
  supporters, donors, or asks to create/edit Cambuildr content. Use the
  cambuildr MCP tools; every tool name is kebab-case (list-content,
  instruct-assistant, create-landing-page). Two-step rule: every create-* tool
  returns an empty entity — always follow up with instruct-assistant to
  populate it. Bind a triggered mail's firing event with list-trigger-actions
  plus set-trigger-action, never with free-text action names.
version: 0.5.0
---

# Cambuildr

Cambuildr is a Laravel-based CRM for non-profits and campaigns. The MCP server lets Claude read and manage the tenant's **people / supporters**, **target audiences (groups)**, **tags and custom fields**, **landing pages** (editor-built and externally authored), **campaign emails** (scheduled broadcasts), **triggered emails** (event-driven single mails), **workflows** (multi-step automations) and the **media library**.

The server exposes **48 tools, 5 prompts and 4 resources**.

## Tool names are kebab-case

The server derives every tool name from its class name in kebab-case: `list-target-audiences`, `instruct-assistant`, `set-workflow-graph`. PascalCase spellings do not exist and will not resolve. When unsure of a name, read the `cambuildr://tools` resource — it lists the exact wire names this tenant has.

## Prefer the server-side prompts

The server ships five guided prompts. They carry the same workflows this skill describes, stay in step with the tools automatically, and reach every MCP client. Use one when it matches the request instead of improvising the sequence:

| Prompt | Use when |
|---|---|
| `build-landing-page-workflow` | The user wants a new landing page. |
| `build-automated-mail-workflow` | The user wants an automated / triggered / "sent when X happens" email. |
| `build-target-audience-workflow` | The user wants a segment, group or target audience. |
| `build-workflow-automation` | The user wants an automation, a journey, or a multi-step "when X, then Y, wait, then Z" flow. |
| `audit-tenant-content` | The user asks what exists, wants an overview, or asks what needs attention. |

## Resources

Read-only tenant reference data. Attach one once rather than re-fetching through tools every turn.

| Resource | URI | Contents |
|---|---|---|
| Tool catalog | `cambuildr://tools` | The exact wire names of every tool, prompt and resource this tenant has. Authoritative. |
| Tenant profile | `cambuildr://tenant` | Tenant name, public base URL, content languages, the MCP feature flags in effect, and whether write access and the AI assistant are available. |
| Trigger action catalog | `cambuildr://trigger-actions` | The internal `name.context` trigger action keys, grouped by category. |
| Workflow building blocks | `cambuildr://workflows/{workflow_id}/building-blocks` | Valid node kinds, action types and shapes, plus the tenant's real automated-mail, tag and campaign ids for one workflow. |

## Critical rule — two-step content workflow

Every `create-*` tool returns an entity with an **empty body**. The next step is **always** `instruct-assistant` with the matching `entity_type` and a natural-language instruction. Never tell the user "the landing page / email / audience is done" before `instruct-assistant` has run.

| Step | Tool | Purpose |
|------|------|---------|
| 1 | `create-landing-page` / `create-campaign-mail` / `create-trigger` / `create-target-audience` / `create-workflow` | Scaffold the entity. Returns id + admin URL. Body, rules or graph are empty. |
| 2 | `instruct-assistant(entity_type, entity_id, instruction)` | Populate it via natural language. **Mandatory.** |
| 3 | `update-*` / `set-*` | Bind audiences and tags, set the trigger action, set the workflow graph, configure delay, publish, activate. |

Use `update-*` for **entity metadata**. Use `instruct-assistant` for **the content** — body, subject, preheader, audience filter rules, workflow graph.

## Tool reference (48 tools)

### Read (23)

| Tool | Purpose |
|------|---------|
| `list-content` | List landing pages / campaign mails / triggers / pages. Optional `type` (`landing_page`, `campaign_mail`, `trigger`, `page`) and `search`. Paginated. |
| `list-people` | Paginated people search. Filter by `target_audience_id` and `search` (name / surname / email). Optional `custom_fields` (array of ids or names, or `["*"]` for every tenant field) — capped at 50 fields per call; `["*"]` errors on a tenant with more than 50 custom fields, so list them explicitly in batches there — and `include_utm` (adds `utm_first_touch` / `utm_last_touch`). With `target_audience_id` set, this is the replacement for the admin CSV-export round trip — page through it instead. |
| `list-target-audiences` | Non-archived target audiences with name, description and people count. Paginated. |
| `list-tags` | The tenant's tags, consentable ones included. Tag ids are what `update-campaign-mail`'s `tag_ids` and a hosted signup form's `tags[]` input expect. Paginated. |
| `list-custom-fields` | The tenant's custom fields with their type and, for select-style fields, their allowed values. Paginated. |
| `list-trigger-actions` | The internal trigger action catalog. No arguments returns the `name.context` keys grouped by category; `action` returns that key's valid sources; `action` plus `source_id` returns the valid classes/answers (and the selectable Stripe products for purchase actions). |
| `list-workflows` | The tenant's automation workflows: id, name, description, active state, re-enrollment policy, and whether a graph version is published. Filter by `search` and `active`. Paginated. |
| `list-mail-senders` | The tenant's mail senders with `ready_to_send`. Gives the ids `update-campaign-mail-variant`'s and `update-trigger-variant`'s `mail_sender_id` expect. Paginated. |
| `list-content-versions` | A landing page / campaign mail / trigger variant's saved body versions, newest first: `id`, `created_at`, `saved_by_user_id`, `source` (`user` or `assistant`). Paginated. |
| `list-person-actions` | One person's action timeline: `name`, `vendor`, `context`, `created_at`, and per-action UTM parameters. Paginated, newest first. |
| `get-landing-page` | Full landing-page details: name, description, page title, publish state, slug, variants (now with `body_updated_at`), tags, plus `goal` (the user's goal, or the AI-inferred one when none is set) and `goal_source` (`user`, `inferred` or `none`). |
| `get-campaign-mail` | Full campaign-mail details: state, planned date, A/B test settings, target audiences, tags, and variants with `name`, `subject`, `preheader`, `reply_to`, `mail_sender_id`, `sender`, `body_updated_at`, `validation_state` (`INITIALIZING`, `RUNNING`, `FAILED` or `COMPLETED`) and `ready_to_send` (`email_subject` still returned as a deprecated alias for `subject`). `update-campaign-mail-variant`, `restore-content-version` and an assistant edit all re-run this validation in the background — re-read `get-campaign-mail` and wait until `ready_to_send` is `true` before `send-test-mail`. |
| `get-trigger` | Full triggered-mail details: active state, action configuration, delay settings, and variants with their subject, sender, content and `body_updated_at`. |
| `get-target-audience` | Target-audience details: people count, computation state, archive status, `is_legacy`, and the filter `rules` themselves as `{include, exclude}` plus a plain-language `rules_summary`. `rules` is `{include: [], exclude: []}` for an empty (ruleless) audience — it is `null` only for a legacy audience (`is_legacy: true`), one built before the current rule format. |
| `get-workflow` | One workflow: metadata, the current published graph, its start condition, and the building blocks a graph may reference. **Call this before `set-workflow-graph`.** |
| `get-hosted-landing-page-contract` | The authoring contract for externally authored pages. An optional `landing_page_id` adds that page's variant ids and existing signup forms. |
| `get-content` | Read a landing page / campaign mail / triggered mail variant's body as `outline`, `text` (mails: as-sent plain text) or the stored `html` (merge tags left unresolved — `{{ var:firstname }}`, not a filled-in value). Returns `preview_url` and `body_updated_at` alongside the content. `preview_url` is the authenticated admin preview: it opens for a human in a logged-in browser tab, but an agent cannot fetch it directly. Read this before editing, and again after `instruct-assistant` to see what changed. |
| `get-assistant-run` | Poll an `instruct-assistant` run by the `run_id` it returned: `status`, the assistant's message once complete, and any error. |
| `get-action-utm-breakdown` | The admin "action → UTM" report: one action's people, broken down by a chosen UTM parameter (`utm_source` by default) over a date range, with optional drill-in to the people behind one value. |
| `read-person` | One person record: name, email, tags, addresses, donation summary, every custom field the person has a value for, and `utm_first_touch` / `utm_last_touch`. Takes no `custom_fields` parameter — unlike `list-people`, there is no field selection; you always get all of them. |
| `search-media-library` | Search the media library by `query`, `folder` and `kind` (`image` / `document`). Returns each match with its first-party URL. Paginated. |
| `search` | One text query across landing pages, campaign mails, triggered mails, target audiences, workflows and people. Returns a short list, each row carrying a composite id (`landing_page:42`), a title and an admin URL. Exists because some clients — ChatGPT's connector among them — drive a server through a `search`/`fetch` pair rather than per-type tools. Prefer `list-content` / `list-people` when you want pagination and full rows. |
| `fetch` | One record in full, by a composite id `search` returned. The other half of the same pair. |

### Write — core entities (12)

| Tool | What's possible | What's NOT possible |
|------|------------------|----------------------|
| `create-landing-page` | Create an empty editor landing page: `name`, `description`, `page_title`, `goal` (what the page should achieve, in one or two sentences; read by the admin and the assistant). Returns id + admin URL. | No body, share metadata or publish state. Body goes through `instruct-assistant`, metadata through `update-landing-page`. |
| `update-landing-page` | `name`, `description`, `page_title`, `share_title`, `share_description`, `is_published`, `goal` (what the page should achieve, in one or two sentences; read by the admin and the assistant). Returns `goal` and `goal_source` like `get-landing-page`. | Cannot edit the body. Cannot manage variants or tags. |
| `create-campaign-mail` | Create a campaign mail in `EDITING` state: `name`, `description`. Returns id + admin URL. | No subject, preheader, audience, planned date or body. |
| `update-campaign-mail` | `name`, `description`, `group_ids` (target audiences), `tag_ids`, and the A/B test settings `test_duration`, `test_percent`, `winning_selection`. Only while in `EDITING` — fields that do not apply outside `EDITING` now return an error instead of being silently dropped. | Cannot advance state or set the planned date. Cannot edit the body. |
| `update-campaign-mail-variant` | Set a campaign mail variant's `name`, `subject`, `preheader`, `reply_to` and `mail_sender_id` directly — no `instruct-assistant` call needed for these fields. `id` plus `variant_id`. Only while in `EDITING`. | Cannot edit the body. |
| `create-trigger` | Create a triggered mail, inactive: `name`, `description`, and optionally the action binding. Returns id + admin URL. | Body empty. Stays inactive until `update-trigger active=true`. Do not pass a hand-written action name — see the trigger section below. |
| `update-trigger` | `name`, `description`, `active`, `delay` plus `delay_days` and `delay_time` (`HH:MM`). | Cannot edit the body. The action binding belongs to `set-trigger-action`; subject/preheader/sender belong to `update-trigger-variant`. |
| `update-trigger-variant` | Set a triggered mail variant's `name`, `email_subject`, `preheader`, `reply_to` and sender (`mail_sender_id`, or `sender_name`/`sender_email`) directly. `id` plus `variant_id`. | Cannot edit the body. |
| `set-trigger-action` | Set or replace the firing event of an existing triggered mail: `action` (a `name.context` key) plus `source_id`, `class_id` and `product_ids` where applicable. | Values must come from `list-trigger-actions`; do not invent them. |
| `create-target-audience` | Create an empty target audience: `name`, `description`. Returns id + admin URL. | **The group has no filter rules and therefore matches nobody.** Rules go through `instruct-assistant`. |
| `update-target-audience` | `name`, `description`. | Does not touch filter rules or archive state. |
| `add-media-library-item` | Download a public `url` into the tenant's own storage under a hosted page's assets folder (`landing_page_id` required, optional `name`). Returns the first-party URL. | You do not choose the folder. Search first — do not re-add what the tenant already has. |

### Write — content (3)

Apply to landing pages, campaign mails and triggered mails alike (`entity_type` is `landing_page`, `campaign_mail` or `trigger`).

| Tool | What's possible | What's NOT possible |
|------|------------------|----------------------|
| `duplicate-content` | Duplicate a campaign mail, triggered mail or landing page. Takes only `entity_type` and `entity_id` — no `variant_id` (it copies every variant). Returns the new id, its variants and admin URL. Make a safe copy before a risky rewrite. | Does not itself edit either copy — the new one starts identical to the source. |
| `restore-content-version` | Restore one of `list-content-versions`' saved versions onto the live variant (`variant_id` required, for landing pages, campaign mails and triggered mails alike). Non-destructive: the restore itself is snapshotted as a new version, so it is never a one-way trip — an assistant edit can always be undone this way, because the pre-edit body is saved as a version before a variant's first assistant edit. Campaign mails only while `EDITING`. | Does not restore a target audience's rules or a workflow's graph — neither is versioned this way. |
| `send-test-mail` | Send a test of a campaign mail or triggered mail variant to the token owner, or another admin user of the tenant. At most 5 recipients per call, 10 test mails per hour per user. For a campaign mail, wait until the variant's `ready_to_send` is `true` (re-read `get-campaign-mail`) first. | Cannot send to an arbitrary address — recipients must be administrators of the tenant. Refused when mail sending is disabled for the tenant. |

### Write — workflows (4)

| Tool | What's possible |
|------|------------------|
| `create-workflow` | Create an **empty** workflow: `name`, `description`, optional `campaign_id`. Inactive, no graph, no start condition. |
| `set-workflow-start-condition` | Set (replace) the single event that enrolls a person: `action` (a `name.context` key from `list-trigger-actions`) plus `source_id`, `class_id`, `subclass_id`, `product_ids` and a `value_min` / `value_max` range where applicable, and `allow_automation_origin` to opt into cascades. |
| `set-workflow-graph` | Replace the graph with the **complete** set of `nodes` and `edges` and publish it as a new version. |
| `update-workflow` | `name`, `description`, `reenrollment` (`ONCE` / `EVERY_TIME`), `active`. |

### Write — hosted (externally authored) landing pages (4)

| Tool | What's possible |
|------|------------------|
| `create-hosted-landing-page` | Create a page whose content is raw HTML: `name`, `description`, `page_title`, `goal` (what the page should achieve, in one or two sentences; read by the admin and the assistant), optional `body_html`. Returns the page id, the default variant id and the public URL. |
| `set-hosted-landing-page-content` | Replace one variant's `body_html`. Defaults to the first variant. Rejected on editor pages. |
| `create-hosted-landing-page-variant` | Add an A/B variant with its own `body_html`, optional `name`, `is_published`, and `starts_at` / `ends_at` (ISO 8601). |
| `create-hosted-landing-page-signup-form` | Define a signup form for a hosted variant. Returns the form id, the submit endpoint and a field schema to render a plain HTML form against. |

### AI content (2)

`instruct-assistant(entity_type, entity_id, variant_id?, instruction)`.

- `entity_type` is one of `landing_page`, `campaign_mail`, `trigger`, `target_audience`, `workflow`.
- `instruction` is natural language, up to 10,000 characters.
- `variant_id` is optional and applies **only** to `landing_page`, `campaign_mail` and `trigger`; the first variant resolves automatically when it is omitted. Triggered mails no longer need one passed explicitly. Passing it for `target_audience` or `workflow` is an error.

What the assistant does per entity type:

| `entity_type` | Effect |
|---|---|
| `landing_page` | Edits the editor (BeeFree) content body — sections, text, styling, layout. |
| `campaign_mail` | Edits the email body, plus subject and preheader. |
| `trigger` | The same as `campaign_mail`, plus the trigger's action-specific placeholders. |
| `target_audience` | Rewrites the audience's **filter rules**. |
| `workflow` | Rewrites the automation **graph**. |

For a `campaign_mail` or `trigger`, `instruct-assistant` is for the **content** — body, subject, preheader. If all you need is the subject, preheader, reply-to or sender, `update-campaign-mail-variant` / `update-trigger-variant` set them directly, faster and without spending AI credits.

**`instruct-assistant` runs asynchronously.** It waits up to about 40 seconds for the run to finish. A run that finishes in time returns `{status: "success", run_status: "completed", run_id, assistant_message, …}`. A run that takes longer returns `{status: "running", run_status: "pending"|"running", run_id, poll_with: "get-assistant-run", message}` instead — that is not a failure. Poll `get-assistant-run(run_id)` (its `status` moves through `pending` → `running` → `completed`/`failed`), or re-call `instruct-assistant` with the exact same `idempotency_key` and arguments — that works even if AI credits have since run out, and this is itself a valid way to poll for a client that has no `get-assistant-run`. **Always pass an `idempotency_key`** (any string unique to this edit) on every call: it means a retry after a timeout can never apply the same edit twice. A run that ends `failed` stays failed under that key forever — to try again, use a **new** `idempotency_key`. Only one run per entity (and variant) can be in progress at a time; a second call while one is running is refused, naming the run already in progress.

A run's edits apply straight to the **live** landing page / mail / trigger content — there is no separate "working copy" to publish, and `conversation_id` is `null` by design. Use `get-content` (and `list-content-versions` if you need history) to see what actually changed after a run completes.

**`instruct-assistant` is registered only when the tenant has opted in to the AI assistant.** If the tenant has not, the tool is simply **absent from the tool list** while every other tool keeps working. That is not an error to retry: say so plainly and offer the paths that do not need it — hosted HTML pages, metadata-only updates, or editing in the Cambuildr admin UI.

`instruct-assistant` also spends AI credits. When the balance is exhausted the call returns an error saying so; the fix is a top-up, not a retry.

### Checking a landing page

`check-landing-page(landing_page_id, variant_id?, goal?)` runs an AI review of one landing page variant against its goal — call to action, message, structure, trust, sharing metadata, goal fit, feature fit — and returns a deterministic score from 0-100 plus findings, each with a suggested fix. Call it after `instruct-assistant` has set the content and before publishing.

- `variant_id` defaults to the first published variant, or failing that the first variant.
- `goal`, when given, is saved as the page's goal (same field `update-landing-page`'s `goal` writes) and the review judges the page against it; otherwise the page's already-saved or inferred goal is used.
- Runs synchronously and can take up to a minute. Spends AI credits on every call.
- Every finding carries one of the categories `cta`, `message`, `structure`, `trust`, `sharing`, `goal_fit`, `feature_fit`, `accessibility`. `accessibility` findings only ever come from a check started in the Cambuildr admin UI.
- A `feature_fit` finding says the page's goal calls for a Cambuildr block the page is not using — a donation block for a fundraising page, a supporter block for a petition — and names that block in `location.block_type`. That is the same block id `instruct-assistant` takes, so the fix is a follow-up `instruct-assistant` call, not a question back to the user about what the block is called.
- Because it runs synchronously it reviews the page's content only: it skips the screenshot, dead-link, page-speed and accessibility passes an admin-triggered check makes, so it makes no pixel judgement — nothing about how the page renders, how it looks on a phone, broken links, page speed, alt text, headings, colour contrast or font size. It *does* report the document's own ordering, so a call to action written far down the page is still flagged.
- **Registered only when the tenant has both the AI opt-in and the `ai_page_check` feature enabled** — narrower gating than `instruct-assistant`, which needs only the opt-in. Missing from the tool list means one of those two is off, not a connection problem.

## Capability matrix — what each `entity_type` can build

### Standard blocks (available in all three content types)

Text, Paragraph, Heading, Button, Image, Video, Spacer, Divider, Icons, Social, List, Menu, raw HTML. Rows and columns with mobile-responsive overrides.

### Custom blocks — availability per entity type

| Block | `landing_page` | `campaign_mail` | `trigger` | Notes |
|-------|:--------------:|:---------------:|:---------:|-------|
| Countdown timer | Yes | No | No | Landing-page-only. |
| Signup form (multi-field, multi-step, opt-in / GDPR disclaimer) | Yes | No | No | Landing-page-only. |
| Donation block (preset amounts, anonymous, address gating, tax-deduction text) | Yes | No | No | Landing-page-only. |
| Purchase block (Stripe) | Yes | No | No | Landing-page-only. |
| Survey — POLL (multiple choice, 2-4 answers) | Yes | Yes | Yes | The only survey type that works in emails. |
| Survey — SENTIMENT / MULTI_SWIPE / VERIFIED_VOTING | Yes | No | No | Landing-page-only. |
| Share block (mail, Facebook, X, LinkedIn, WhatsApp, Telegram, Threads, Bluesky) | Yes (URL defaults to the page) | Yes (URL required) | Yes (URL required) | |
| Progress bar (source SIGNUPS / DONATIONS / GROUP) | Yes | No | No | Landing-page-only. |
| Event / Commitment / UGC teaser | Yes | No | No | Needs an existing page of that type. |

### Entity-type-specific knobs (also edited via `instruct-assistant`)

| Knob | `landing_page` | `campaign_mail` | `trigger` |
|------|:---:|:---:|:---:|
| Page title (browser tab) | Yes | No | No |
| Share title / share description | Yes | No | No |
| URL slug / page language | Yes | No | No |
| Email subject | No | Yes | Yes |
| Email preheader | No | Yes | Yes |

### Personalisation / merge tags (emails only)

**Landing pages never resolve `var:` tags.** The one exception is `{{ var:prefill_link }}` in a URL, covered below — everywhere else on a landing page, a `var:` tag is used as a literal URL query parameter name, not substituted.

#### Basic syntax

- A placeholder is `{{ var:placeholder_name }}` — double curly braces, the literal `var:` prefix, then a snake_case name. Whitespace inside the braces is fine; the `var:` prefix is not optional.
- **There is no `#` prefix.** `#{{ var:firstname }}` is not valid syntax — `#` is a regular-expression delimiter that shows up in Cambuildr's own source and logs, never something to write in a brief or in email content. Write `{{ var:firstname }}`.
- Usable in headings, paragraphs, buttons, subject lines, preheaders and link URLs.
- **Campaign mail**: person fields, customer fields, custom fields.
- **Trigger**: the same, **plus** action-specific placeholders derived from the bound trigger action (a donation amount on a donation action, event data on event actions). The assistant introspects the available list at runtime — describe what you want rather than guessing tag names.
- The most common tags — `firstname`, `lastname`, `email`, `unsubscribe_url`, `unsubscribe_one_click_url` — are always available without a lookup; everything else needs the assistant to check the live placeholder list for that entity first.
- Internal links in emails are auto-prefixed with the tenant's base URL by the agent.

#### Fallback

`{{ var:placeholder_name:fallback text }}` prints the fallback when the value is empty. One tag instead of a conditional for a simple greeting: `Hallo {{ var:firstname:Freund }}`.

#### Conditionals

Both campaign mails and triggered mails support showing or hiding content per recipient:

```
{% if var:firstname:false %}Hallo {{ var:firstname }},{% else %}Hallo,{% endif %}
```

- `:false` is the idiom for "does this value exist": `var:firstname:false` reads as the value, or the literal `false` when the field is empty — and `false` itself counts as not set.
- Tags: `{% if %}` `{% elseif %}` `{% else %}` `{% endif %}`. Every `{% if %}` must be closed by its own `{% endif %}` in the same block of content — never opened in one block and closed in another.
- Comparison operators: `===` `==` `!=` `<>` `<=` `>=` `=` `<` `>`.
- Logical operators: `and` `or` `not` `xor`.
- Functions, wrapping a value: `Upper()` `Lower()` `Capitalize()` `Escape()`.
- This is the subset both the campaign-mail renderer (Mailjet) and the triggered-mail renderer (evaluated in-house) agree on — it is deliberately narrower than full Mailjet template syntax, so anything on this list works the same way in both mail types.
- Leave a conditional the user already wrote alone unless they ask you to change it — it is valid syntax, not a mistake to correct.

#### Invalid forms — never produce these

These look plausible but are not valid, and render as literal text (or are stripped) instead of being substituted:

- `{{firstname}}`, `{{ first_name }}`, `{{name}}`, `{{user.email}}` — missing the `var:` prefix.
- `#{{ var:firstname }}` — no `#` prefix exists; see above.
- `{firstname}`, `{{{firstname}}}` — wrong brace count.
- `%firstname%`, `${firstname}`, `[firstname]` — delimiter styles from other template systems.
- `{{ var:firstName }}`, `{{ var:user.first_name }}` — placeholder names are snake_case, no camelCase, no dots.
- `{% for %}`, `{% set %}` — not supported tags.
- Arithmetic (`+ - * / div mod`) and dot notation (`{{ var:a.b }}`) inside a conditional.
- `Round()`, `Int()`, `UrlEncode()`, `FormatNumber()`, `FormatNumberLocale()` — Mailjet functions this pipeline does not implement.
- The `data:`, `segment:` and `mj:` namespaces — Mailjet-side concepts with no `var:`-style counterpart here.

#### Linking to a Cambuildr landing page and prefilling its form

Use `{{ var:prefill_link }}` as the **entire query string**: `https://<tenant-domain>/<page>?{{ var:prefill_link }}`. It resolves to a signed, short-lived token — not the recipient's raw data — so nothing personal travels in the URL.

Do not spell the prefill out as separate placeholders (`?firstname={{ var:firstname }}&email={{ var:email }}`). Putting a person variable (`{{ var:email }}`, a name, a custom field) directly inside a link still works, but the editor shows a non-blocking warning, because the value then travels in the URL where analytics, server logs and the destination's own tracking can read it — reserve that for a link to an external system that genuinely needs the raw value.

### Styling rules the agents enforce

- Colors: hex only (`#ffffff`, `#0B1020`), 8-digit hex for opacity, plus `transparent` and `inherit`. No `rgba()`, `rgb()` or `hsl()`.
- Pixel values only.
- Rows must declare their background properties explicitly.

## Triggered mails — bind a real firing event

This is the single most common way to produce an automation that looks live and never runs.

`create-trigger` and `set-trigger-action` accept two mutually exclusive kinds of binding:

- **Internal Cambuildr action** — the default. `action` is a dotted `name.context` key that exists in the tenant's catalog: `signed-up.campaign`, `donated.donation`, `has-birthday.database`, `submitted.survey`. This is what fires on real Cambuildr events.
- **External / webhook action** — requires an explicit `is_internal_action: false`. `action_name`, `action_context` and `action_source` are then free text describing an event pushed in from another system. **No internal Cambuildr event will ever fire it.**

A hand-written action name is a webhook binding, not a signup binding. Never guess one. The correct sequence:

1. `create-trigger` with the name and description only.
2. `list-trigger-actions` with no arguments for the catalog of `name.context` keys.
3. `list-trigger-actions` with `action` for that key's sources, then with `action` plus `source_id` for its classes/answers. `source_id: 0` means "any"; `class_id: 0` means "any" and `-1` means sentiment "undecided".
4. `set-trigger-action` with `id`, `action`, and the `source_id` / `class_id` / `product_ids` you resolved.
5. `instruct-assistant` with `entity_type: trigger` to write the body, subject and preheader.
6. `update-trigger` with `active=true` — last, once the body looks right.

Choose an external binding only when the user says the event comes from another system, and then set `is_internal_action: false` deliberately.

## Target audiences — the rules step is mandatory

`create-target-audience` returns a group **with no filter rules, matching nobody**. It is not a usable segment until the rules exist.

1. `create-target-audience` with `name` and `description`.
2. `instruct-assistant` with `entity_type: target_audience` and a natural-language description of who belongs in it ("everyone who donated more than 50 euros in the last year and is not already tagged Major Donor").
3. `get-target-audience` to read back the people count and the computation state, and report the count to the user. It also returns the rules themselves — `rules: {include, exclude}` plus a plain-language `rules_summary` — and `is_legacy` for an audience built before the current rule format. Use these to check what the assistant actually wrote, not just how many people matched.

Rule authoring over MCP runs through `instruct-assistant`, so it needs the tenant's AI opt-in. Without it, rules have to be built in the admin UI.

## Workflows (Automations)

A workflow is a multi-step automation: one enrolling event, then a graph of actions, waits and conditions. A triggered mail sends exactly one email on one event; a workflow can send several, tag, wait, branch, call a webhook and more.

### Build order

1. `create-workflow` — inactive, no graph, no start condition.
2. `set-workflow-start-condition` — the single event that enrolls a person. Discover valid values with `list-trigger-actions`, the same catalog the triggered-mail tools use.
3. `get-workflow` — read the building blocks: valid node kinds, action types and shapes, and the tenant's real automated-mail, tag and campaign ids.
4. Write the graph, either with `instruct-assistant` (`entity_type: workflow`, natural language) or with `set-workflow-graph` (explicit nodes and edges).
5. `update-workflow` with `active=true` — last.

### The graph write is a full replace

`set-workflow-graph` replaces the graph with what you send. It is never a diff. Always send **every** node and **every** edge, including the ones you are not changing. Read the current graph with `get-workflow` first and edit that.

- Node kinds: `START`, `ACTION`, `CONDITION`, `WAIT`. Exactly one `START` node is required.
- Only `CONDITION` nodes may have more than one outgoing edge; their out-edges are labelled `branch: "yes"` and/or `branch: "no"`, at most one of each and no other value. There is no `else` branch: leave a branch unwired and the run simply ends on that side. An edge that does not leave a `CONDITION` carries no branch.
- Action types cover sending an automated mail, attaching a tag, adding to a campaign, writing person data, updating person state, adding an action to a person, calling a webhook, and deleting a person.
- A wait node is either a duration or an absolute date.
- Webhook URLs must be HTTPS on port 443 and resolve to a public address; localhost, private ranges and cloud metadata endpoints are refused.
- A secret webhook header value comes back from `get-workflow` as a sentinel placeholder. **Send that sentinel back unchanged** to keep the stored credential; replacing it overwrites the credential with whatever you sent.
- An invalid graph is rejected with its error codes and nothing is saved.

### Activation

`update-workflow` with `active=true` switches the workflow on — except when the graph contains a **delete person** action. Only Cambuildr can activate one of those. The tool then returns a refusal saying a review has been requested, and the Cambuildr team is notified. That is the designed outcome, not a failure: tell the user their workflow is awaiting Cambuildr review, and do not retry.

### Re-enrollment

`update-workflow`'s `reenrollment` is `ONCE` (a person enrolls at most once, ever) or `EVERY_TIME` (a person may re-enroll after a previous run has ended).

## Hosted (externally authored) landing pages

**Experimental.** Cambuildr can host a landing page whose content is raw HTML you author, instead of an editor (BeeFree) page. The page still gets variant logic, signups and metrics, but it has no editor — its HTML is managed only through these tools, and none of the custom blocks above apply to it.

Pick a hosted page when the user wants full control over the markup, or a page built without the AI assistant. Pick a normal `create-landing-page` otherwise: that is the path with donation blocks, surveys, progress bars and teasers.

### Build order

1. `get-hosted-landing-page-contract` — **first, always.** It states what Cambuildr injects for you, the asset rules, and the endpoint conventions.
2. `create-hosted-landing-page` with a complete HTML document as `body_html` (or without it, and set the content later).
3. `create-hosted-landing-page-signup-form` if the page collects signups. It returns the submit endpoint and a field schema; render inputs whose names match that schema.
4. `set-hosted-landing-page-content` to iterate, `create-hosted-landing-page-variant` to A/B test.

### Authoring rules

- Submit a single, complete HTML document with `<html>`, `<head>` and `<body>`. One missing a `<head>` or `<body>` is rejected.
- Inline your CSS and JavaScript.
- Do **not** embed cookie consent, analytics, pixels, Alpine.js, fonts, icons, meta tags or the tenant's global scripts. Cambuildr injects all of them on render; embedding them duplicates them.
- Third-party libraries must come from the proxied CDN hosts the contract lists, as specific versioned self-contained files. Assets a library fetches at runtime are not proxied.
- Images must be first-party media library URLs. No arbitrary external image URLs, no base64 data URIs. Inline SVG is fine.
- Donation, survey, progress bar, countdown and share blocks are **not** authorable on hosted pages yet.

## Media library

- `search-media-library` before adding anything. A page may reference any item the tenant already has, wherever it lives in the library.
- `add-media-library-item` downloads a public HTTP(S) URL into the tenant's own storage and returns the first-party URL to reference. It takes a `landing_page_id`, not a folder: the file is filed automatically under that page's own assets folder, so machine-added files stay out of the folders the tenant curates by hand.
- Only first-party URLs may be referenced from a hosted page.

## Tags and custom fields

- `list-tags` gives the tag ids for `update-campaign-mail`'s `tag_ids`, for a hosted signup form's `tags[]` input, and for workflow tag actions. Consentable tags are included.
- `list-custom-fields` gives custom field ids and types, with allowed values for select-style fields. These are what a hosted signup form's `custom_fields[]` input expects.
- Look ids up; never guess them.

## Campaign mail vs triggered mail vs workflow

| | Campaign mail | Triggered mail | Workflow |
|---|---|---|---|
| Admin UI label | **Campaign Emails** | **Automated Emails** | **Automations** |
| Starts on | A scheduled date | One bound action | One bound action (the start condition) |
| Does | Sends one broadcast | Sends one email | Runs a graph: mails, tags, waits, conditions, webhooks |
| State | `EDITING` to `READY` to `RUNNING` to `SENT` | `active: false / true` | `active: false / true` |
| A/B testing | Yes | No | No |
| Delay | n/a | Optional (`delay_days` plus `delay_time`) | Explicit `WAIT` nodes |
| Activation | The user advances state in the admin UI | `update-trigger active=true` | `update-workflow active=true` |
| Typical use | Newsletters, announcements, one-off blasts | Signup confirmations, donation thank-yous, birthday greetings | Onboarding journeys, multi-step nurture, re-engagement, branching flows |
| User-speak | "send a newsletter on Friday", "blast the supporters", "schedule an email" | "thank donors automatically", "welcome new signups", "birthday email" | "when someone signs up, wait 3 days, then...", "a journey", "an automation" |

## Recommended flows

### Read before you edit

Before any `instruct-assistant` call on existing content, call `get-content` first so you know what is actually there — a brief written against a guess at the current body produces edits that fight the real one.

1. `get-content(entity_type, entity_id, variant_id?, format: "outline")` — see what exists now.
2. If the edit is risky (a large rewrite, something the user might want to undo), `duplicate-content(entity_type, entity_id)` first and edit the copy — or rely on `list-content-versions` / `restore-content-version` afterwards instead. Either is fine; duplicating is safer when the user might want to compare old and new side by side, restoring is enough when a plain undo is all that's needed. An assistant edit can always be undone this way even without duplicating first: before a variant's very first assistant edit, its pre-edit body is automatically saved as a version, so `restore-content-version` always has something to go back to.
3. `instruct-assistant(...)` with an `idempotency_key` — always, so a timeout-and-retry can never double-apply the edit.
4. `get-content` again to review what changed (or `list-content-versions` to see the new version was recorded).
5. For a campaign mail, re-read `get-campaign-mail` and wait until the variant's `ready_to_send` is `true` — the edit re-triggers validation in the background. Then `send-test-mail` for a campaign mail or trigger, before telling the user it's ready.

### Set subject or sender without the assistant

If all that changed is the subject, preheader, reply-to or sender, skip `instruct-assistant` entirely — call `update-campaign-mail-variant` or `update-trigger-variant` directly. It is faster, does not spend AI credits, and cannot touch the body.

### Analyse a target audience

To look at who is actually in an audience, not just how many:

```
list-people(target_audience_id=<id>, custom_fields=["*"], include_utm=true)
```

Paginate through it — this is the direct replacement for exporting the audience to CSV and reading that. Add `search` to narrow by name/surname/email within the audience.

## Patterns

- **Before writing, list — before editing, get.** `list-*` for context, `get-*` to inspect, `update-*` / `set-*` only after the `get-*` confirms the state.
- **`instruct-assistant` for body content, `update-*` for metadata.** Audience binding, publish flag, trigger delay, active flags, re-enrollment, subject, preheader, reply-to and sender are `update-*` (`update-campaign-mail-variant`, `update-trigger-variant`). Body content, audience rules and the workflow graph are `instruct-assistant`.
- **Never leave a `create-*` call as the last step.** An empty landing page, an unbound trigger, a ruleless audience and a graphless workflow all look created and do nothing.
- **Refuse landing-page-only blocks inside an email.** Donation blocks, signup forms, countdowns, non-POLL surveys, progress bars and teasers do not exist in emails. Offer a landing page carrying the block, linked from the email.
- **Respect tenant tool gating.** A tool the tenant disabled at `/admin/settings/mcp` is not registered at all. If a name you expect is missing, read `cambuildr://tools` rather than retrying. A tenant that has ever saved a custom tool selection there has an explicit allow-list — a newly added tool stays off for them until they enable it, even though it works for every other tenant.
- **Write tools need the write feature flag.** With `ai_mcp_server` but not `ai_mcp_write_access`, only the read tools are registered.
- **Activate last.** `update-trigger active=true` and `update-workflow active=true` come after the content is right.
- **Campaign mails stay in `EDITING`.** Do not promise the mail will send; the user advances it to `READY` in the admin UI.
- **Do not paste large HTML into `instruct-assistant`.** Give it a natural-language brief and let the agent build valid content. Raw HTML belongs on a hosted page, through `set-hosted-landing-page-content`.
- **Re-edit by id.** To iterate, call `instruct-assistant` again with the same `entity_id` and a follow-up instruction.
