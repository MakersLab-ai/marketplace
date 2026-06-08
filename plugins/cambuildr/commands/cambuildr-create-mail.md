---
description: Create a Cambuildr email (campaign broadcast or automated trigger) and populate its content via the AI assistant.
argument-hint: "[campaign|triggered] [name]"
---

# /cambuildr-create-mail

End-to-end workflow: scaffold a Cambuildr email (campaign or triggered) and populate its content body via `InstructAssistant`.

## Step 0 — Resolve the email type

From the first argument, or by asking. Briefly explain the difference if the user is unsure:

- **Campaign mail** ("Campaign Emails" in Cambuildr) → **scheduled broadcast** to a target audience. Has a state machine (EDITING → READY → RUNNING → SENT) and A/B testing. Pick this for newsletters, announcements, one-off blasts.
- **Triggered mail** ("Automated Emails" in Cambuildr) → **event-driven automation**, bound to an action (`signed_up`, `donated`, `accepted-optin`, `recruited`, `clicked`, `has-birthday`, …) and an action context (`campaign`, `landing_page`, …). Pick this for signup confirmations, donation thank-yous, birthday greetings, drip steps.

## Step 0.5 — Set expectations on what's possible in an email

Emails support these blocks (the `full-email` agent):

- Text, headings, images, buttons, video, dividers, lists, menus, raw HTML.
- **POLL survey** (multiple choice, 2–4 answers).
- **Share buttons** (mail, FB, X/Twitter, LinkedIn, WhatsApp, Telegram, Threads, Bluesky) — URL is required.
- **Merge tags** `{{ var:firstname }}`, custom fields, customer fields. Triggered mails additionally get **action-specific placeholders** (e.g. donation amount, event data) — the agent can list them at runtime.

Emails do **NOT** support: signup forms, donation blocks, purchase blocks, countdowns, multi-type surveys (SENTIMENT / MULTI_SWIPE / VERIFIED_VOTING), progress bars, event/commitment/UGC teasers. If the user asks for any of these, stop and explain — offer to make a landing page instead and link to it from the email.

## Path A — Campaign mail

### Step 1 — Gather inputs
- **Name** (use arg if given).
- **Description** (internal, optional).
- **Subject line** (required for the actual send).
- **Preheader** (inbox preview text).
- **Sender** (informational — sender identity is configured at the account level in Cambuildr).
- **Target audience(s)**. Call `ListTargetAudiences` and present options. Collect the chosen `group_ids` (array).
- **Optional tags** (`tag_ids`).
- **Planned date** (informational — actual scheduling happens in the admin UI).
- **Goal / body outline** — what should the email say, in sections?
- **Optional**: POLL survey block (question + 2–4 answers + redirect URL), share buttons.
- **Optional**: merge-tag personalisation (e.g. `{{ var:firstname }}`).

### Step 2 — Scaffold
```
CreateCampaignMail(name=<name>, description=<description>)
```
Capture the returned `id` and admin URL.

### Step 3 — Bind audience + tags
If the user picked any audiences or tags:
```
UpdateCampaignMail(id=<id>, group_ids=[…], tag_ids=[…])
```

### Step 4 — Populate the body via `InstructAssistant`
```
InstructAssistant(
  entity_type="campaign_mail",
  entity_id=<id>,
  instruction="<one detailed brief covering subject, preheader, body sections, any POLL or share blocks, merge tags, style notes>"
)
```

Include the subject and preheader in the instruction text — the email agent has a `SetSubjectAndPreheader` sub-tool that it will call when the brief mentions them.

### Step 5 — Wrap up
Report admin URL. Tell the user the mail is in `EDITING` state — they need to mark it ready in the Cambuildr admin UI when they want to schedule the send. Offer further `InstructAssistant` edits.

## Path B — Triggered mail

### Step 1 — Gather inputs
- **Name** (use arg if given).
- **Description** (internal, optional).
- **`action_name`** — what event triggers this mail? Suggest common values: `signed_up`, `donated`, `accepted-optin`, `recruited`, `clicked`, `has-birthday`. Ask the user to pick one or describe the event.
- **`action_context`** — where does the action happen? Common values: `campaign`, `landing_page`. Ask if it should fire from any context or a specific one.
- **Subject line**.
- **Preheader**.
- **Delay** — should the email be delayed? If yes: how many `delay_days`, and at what `delay_time` (HH:MM)?
- **Goal / body outline** — what should the email say?
- **Merge tags** — mention to the user that triggered mails have access to **action-specific placeholders** (e.g. donation amount for a `donated` trigger, birthday name for `has-birthday`). The assistant agent will list available placeholders at runtime via `GetAvailablePlaceholders`.

### Step 2 — Scaffold
```
CreateTrigger(
  name=<name>,
  description=<description>,
  action_name=<action_name>,
  action_context=<action_context>
)
```
Capture `id` and admin URL. The trigger is **inactive** at this point.

### Step 3 — Populate the body via `InstructAssistant`
```
InstructAssistant(
  entity_type="trigger",
  entity_id=<id>,
  instruction="<brief covering subject, preheader, body sections, merge tags including action-specific ones, any POLL or share blocks>"
)
```

### Step 4 — Configure delay (if requested)
```
UpdateTrigger(id=<id>, delay=true, delay_days=<n>, delay_time="HH:MM")
```

### Step 5 — Activate
Once the body looks good and the user is happy, activate the trigger:
```
UpdateTrigger(id=<id>, active=true)
```
Confirm the trigger is now live and will fire whenever the action occurs.

## What NOT to do

- Do not claim creation is done before `InstructAssistant` has run successfully.
- Do not try to add donation blocks, signup forms, countdowns, progress bars, or non-POLL surveys to emails — those are landing-page-only. Suggest a landing page instead.
- Do not advance a campaign mail's state — that's a manual step in the admin UI.
- Do not flip `active=true` on a trigger until the body is populated.
- Do not invent `action_name` / `action_context` values — ask the user or stick to the common ones above.
