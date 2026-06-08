---
description: Create a Cambuildr landing page and populate it via the AI assistant (supports signup forms, donations, surveys, countdowns, progress bars, teasers, share buttons).
argument-hint: "[name]"
---

# /cambuildr-create-landing-page

End-to-end workflow: scaffold a landing page in Cambuildr, then populate its content body via the `InstructAssistant` MCP tool.

## Step 1 — Gather inputs

If the user passed a name as an argument, use it as the working title. Otherwise ask for one.

Then gather:
- **Description** (internal, optional).
- **Page title** (browser tab; defaults to the name if not given).
- **Goal / CTA** — what is the page for? (collect signups, accept donations, sell a product, run a survey, drive event attendance, …)
- **Which interactive blocks does the user want?** Landing pages support these (emails don't — landing-page-only features):
  - **Signup form** (multi-field, opt-in checkbox, multi-step). If yes, ask which fields (email is always included; common extras: firstname, lastname, phone, address, ZIP, city, country, custom fields, tags). Call `ListTargetAudiences` if the form should put people into a specific group.
  - **Donation block** (3 preset amounts, anonymous donations, tax-deduction text, address gating). Ask for the amounts and the donation purpose.
  - **Purchase block** (Stripe; product title, image, price, currency).
  - **Countdown timer** to a future date/time.
  - **Survey** — POLL (multiple choice 2–4 answers), SENTIMENT (emoji scale 0–10), MULTI_SWIPE (swipe through questions), or VERIFIED_VOTING (email/SMS verified).
  - **Progress bar** sourced from SIGNUPS, DONATIONS, or a GROUP — with an objective number and a label postfix (e.g. "supporters", "€").
  - **Event / Commitment / UGC teaser** (requires an existing Event / Commitment / UGC page ID).
  - **Share buttons** (mail, Facebook, X/Twitter, LinkedIn, WhatsApp, Telegram, Threads, Bluesky).
- **Share metadata** (optional, for social previews): share_title, share_description.

## Step 2 — Scaffold the entity

Call `CreateLandingPage` with:
- `name` — required
- `description` — if provided
- `page_title` — if provided

Capture the returned `id` and admin URL.

## Step 3 — Populate the body via `InstructAssistant`

This is the critical step — `CreateLandingPage` returns an **empty** page. Call:

```
InstructAssistant(
  entity_type="landing_page",
  entity_id=<id from step 2>,
  instruction="<detailed natural-language brief>"
)
```

The instruction should be one block of text that lists every section to build, naming the block types explicitly. Example:

> Hero row with headline "Save the bees" and a short subheading. A paragraph explaining the campaign. A countdown timer to 2026-06-01 18:00. A signup form with fields: email (required), firstname, lastname, opt-in disclaimer with GDPR consent. A donation block with amounts 10€/25€/50€, anonymous donations allowed, tax-deduction text on. A progress bar sourced from DONATIONS with objective 100000 and postfix "€ raised". Share buttons for Facebook, WhatsApp, X. Use a green/blue color palette, large rounded buttons.

## Step 4 — Wrap up

Report:
- The landing page admin URL (for editing/preview).
- Whether share metadata needs setting → if the user provided `share_title` / `share_description`, call `UpdateLandingPage` with those.
- Whether to publish → ask the user; if yes, call `UpdateLandingPage` with `is_published=true`.
- Offer further tweaks: another `InstructAssistant` call for content adjustments.

## What NOT to do

- Do not claim "the landing page is done" before step 3 runs successfully.
- Do not use `UpdateLandingPage` to try to edit the body — that endpoint only changes metadata. Body edits go through `InstructAssistant`.
- Do not invent template IDs or block IDs; let the assistant agent pick them.
