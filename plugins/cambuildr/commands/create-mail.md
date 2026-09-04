---
description: Create a Cambuildr email (campaign broadcast or automated trigger) and populate its content via the AI assistant.
argument-hint: "[campaign|triggered] [name]"
---

# /cambuildr:create-mail

End-to-end workflow: scaffold a Cambuildr email (campaign or triggered) and populate its content body via `instruct-assistant`.

The server ships the triggered path as the `build-automated-mail-workflow` prompt. If the client can run it, prefer that — it is maintained alongside the tools. Use this command otherwise.

## Step 0 — Resolve the email type

From the first argument, or by asking. Briefly explain the difference if the user is unsure:

- **Campaign mail** ("Campaign Emails" in Cambuildr) → **scheduled broadcast** to a target audience. Has a state machine (EDITING → READY → RUNNING → SENT) and A/B testing. Pick this for newsletters, announcements, one-off blasts.
- **Triggered mail** ("Automated Emails" in Cambuildr) → **one email sent when one bound event fires**, with an optional delay. Pick this for signup confirmations, donation thank-yous, birthday greetings.

If the user describes several steps — "send this, wait three days, then tag them and send that" — they want a **workflow**, not a triggered mail. Point them at `/cambuildr:create-workflow`.

## Step 0.5 — Set expectations on what's possible in an email

Emails support these blocks:

- Text, headings, images, buttons, video, dividers, lists, menus, raw HTML.
- **POLL survey** (multiple choice, 2–4 answers).
- **Share buttons** (mail, FB, X/Twitter, LinkedIn, WhatsApp, Telegram, Threads, Bluesky) — URL is required.
- **Merge tags** `{{ var:firstname }}`, custom fields, customer fields. Triggered mails additionally get **action-specific placeholders** (e.g. donation amount, event data) drawn from the bound trigger action — the agent introspects them at runtime, so describe what you want rather than guessing tag names.

Emails do **NOT** support: signup forms, donation blocks, purchase blocks, countdowns, multi-type surveys (SENTIMENT / MULTI_SWIPE / VERIFIED_VOTING), progress bars, event/commitment/UGC teasers. If the user asks for any of these, stop and explain — offer to make a landing page instead and link to it from the email.

## Path A — Campaign mail

### Step 1 — Gather inputs
- **Name** (use arg if given).
- **Description** (internal, optional).
- **Subject line** (required for the actual send).
- **Preheader** (inbox preview text).
- **Sender** (informational — sender identity is configured at the account level in Cambuildr).
- **Target audience(s)**. Call `list-target-audiences` and present options. Collect the chosen `group_ids` (array).
- **Optional tags**. Call `list-tags` for the ids; collect `tag_ids`.
- **Planned date** (informational — actual scheduling happens in the admin UI).
- **Goal / body outline** — what should the email say, in sections?
- **Optional**: POLL survey block (question + 2–4 answers), share buttons.
- **Optional**: merge-tag personalisation (e.g. `{{ var:firstname }}`).

### Step 2 — Scaffold
```
create-campaign-mail(name=<name>, description=<description>)
```
Capture the returned `id` and admin URL.

### Step 3 — Bind audience + tags
If the user picked any audiences or tags:
```
update-campaign-mail(id=<id>, group_ids=[…], tag_ids=[…])
```

### Step 4 — Populate the body via `instruct-assistant`
```
instruct-assistant(
  entity_type="campaign_mail",
  entity_id=<id>,
  instruction="<one detailed brief covering subject, preheader, body sections, any POLL or share blocks, merge tags, style notes>"
)
```

Include the subject and preheader in the instruction text — the email agent sets them when the brief mentions them.

### Step 5 — Wrap up
Report the admin URL. Tell the user the mail is in `EDITING` state — they mark it ready in the Cambuildr admin UI when they want to schedule the send. Offer further `instruct-assistant` edits.

## Path B — Triggered mail

A triggered mail is only real once it is **bound to an internal Cambuildr action**. Getting this wrong is the classic failure: a free-text action name creates an *external webhook* binding that no Cambuildr event ever fires, so the automation looks live and never runs. Discover the binding, don't invent it.

### Step 1 — Gather inputs
- **Name** (use arg if given).
- **Description** (internal, optional).
- **What event should send this mail?** Ask in plain language ("when someone signs up on the spring campaign", "when a donation comes in"). Do **not** ask the user for an action name — you will resolve it in step 3.
- **Subject line**.
- **Preheader**.
- **Delay** — should the email be delayed? If yes: how many `delay_days`, and at what `delay_time` (HH:MM)?
- **Goal / body outline** — what should the email say?
- **Merge tags** — mention that triggered mails have access to action-specific placeholders drawn from the bound action.

### Step 2 — Scaffold
```
create-trigger(name=<name>, description=<description>)
```
Name and description only. Capture `id` and admin URL. The trigger is **inactive** and **unbound** at this point.

### Step 3 — Resolve the firing event with `list-trigger-actions`
```
list-trigger-actions()
```
With no arguments this returns the catalog of internal action keys as dotted `name.context` strings, grouped by category — for example `signed-up.campaign`, `donated.donation`, `has-birthday.database`, `submitted.survey`. Pick the key that matches what the user described; confirm it with them if more than one fits.

Then drill in:
```
list-trigger-actions(action="<key>")                        # valid sources for that key
list-trigger-actions(action="<key>", source_id=<id>)        # valid classes / answers for that source
```
`source_id: 0` means "any". `class_id: 0` means "any"; `-1` means sentiment "undecided". Purchase and Stripe-event actions return selectable products instead of classes.

The `cambuildr://trigger-actions` resource carries the same catalog if you would rather attach it once.

### Step 4 — Bind the action with `set-trigger-action`
```
set-trigger-action(
  id=<id>,
  action="<name.context key>",
  source_id=<resolved source id>,
  class_id=<resolved class id>          # when the action has classes
)
```
Only set `is_internal_action=false` with `action_name` / `action_context` / `action_source` when the user has said the event is pushed in from another system. That is a webhook binding, and no internal Cambuildr event will fire it.

### Step 5 — Populate the body via `instruct-assistant`
```
instruct-assistant(
  entity_type="trigger",
  entity_id=<id>,
  instruction="<brief covering subject, preheader, body sections, merge tags including action-specific ones, any POLL or share blocks>"
)
```
Leave `variant_id` out — the first variant resolves automatically.

Bind the action (step 4) **before** this call, so the assistant sees the action-specific placeholders the binding unlocks.

### Step 6 — Configure delay (if requested)
```
update-trigger(id=<id>, delay=true, delay_days=<n>, delay_time="HH:MM")
```

### Step 7 — Activate
Once the body looks good and the user is happy:
```
update-trigger(id=<id>, active=true)
```
Then verify with `get-trigger` that it reports both `active: true` and the internal action binding you set. Confirm to the user which event will fire it.

## What NOT to do

- Do not claim creation is done before `instruct-assistant` has run successfully.
- Do not pass a hand-written `action` string to `create-trigger` or `set-trigger-action`. Always take the key from `list-trigger-actions`.
- Do not set `is_internal_action=false` unless the user asked for an external webhook. It produces a trigger no Cambuildr event fires.
- Do not try to add donation blocks, signup forms, countdowns, progress bars, or non-POLL surveys to emails — those are landing-page-only. Suggest a landing page instead.
- Do not advance a campaign mail's state — that's a manual step in the admin UI.
- Do not flip `active=true` on a trigger until it is both bound and populated.
