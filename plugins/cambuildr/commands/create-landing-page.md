---
description: Create a Cambuildr landing page and populate it via the AI assistant (supports signup forms, donations, surveys, countdowns, progress bars, teasers, share buttons).
argument-hint: "[name]"
---

# /cambuildr:create-landing-page

End-to-end workflow: scaffold a landing page in Cambuildr, then populate its content body via the `instruct-assistant` MCP tool.

The server also ships this as the `build-landing-page-workflow` prompt. If the client can run it, prefer that — it is maintained alongside the tools. Use this command otherwise.

## Step 0 — Pick the page kind

Two kinds of landing page exist:

- **Editor page** (`create-landing-page`) — the default, and what the rest of this command covers. Content is built by the AI assistant and editable in the Cambuildr editor. This is the only kind that supports donation blocks, signup forms, countdowns, surveys, progress bars and teasers.
- **Hosted page** (`create-hosted-landing-page`) — **experimental**. Raw HTML you author yourself, hosted by Cambuildr with variant logic, signups and metrics, but with no editor and none of the custom blocks. Choose it only when the user explicitly wants full control of the markup, or when `instruct-assistant` is unavailable because the tenant has not opted in to the AI assistant. If you go this way, call `get-hosted-landing-page-contract` first and follow the hosted-page section of the `cambuildr` skill.

## Step 1 — Gather inputs

If the user passed a name as an argument, use it as the working title. Otherwise ask for one.

Then gather:
- **Description** (internal, optional).
- **Page title** (browser tab; defaults to the name if not given).
- **Goal / CTA** — what is the page for? (collect signups, accept donations, sell a product, run a survey, drive event attendance, …)
- **Which interactive blocks does the user want?** Landing pages support these (emails don't — landing-page-only features):
  - **Signup form** (multi-field, opt-in checkbox, multi-step). If yes, ask which fields (email is always included; common extras: firstname, lastname, phone, address, ZIP, city, country, custom fields, tags). Call `list-target-audiences` if the form should put people into a specific group, `list-custom-fields` and `list-tags` if it should write custom fields or set consent tags.
  - **Donation block** (3 preset amounts, anonymous donations, tax-deduction text, address gating). Ask for the amounts and the donation purpose.
  - **Purchase block** (Stripe; product title, image, price, currency).
  - **Countdown timer** to a future date/time.
  - **Survey** — POLL (multiple choice 2–4 answers), SENTIMENT (emoji scale 0–10), MULTI_SWIPE (swipe through questions), or VERIFIED_VOTING (email/SMS verified).
  - **Progress bar** sourced from SIGNUPS, DONATIONS, or a GROUP — with an objective number and a label postfix (e.g. "supporters", "€").
  - **Event / Commitment / UGC teaser** (requires an existing Event / Commitment / UGC page ID).
  - **Share buttons** (mail, Facebook, X/Twitter, LinkedIn, WhatsApp, Telegram, Threads, Bluesky).
- **Images.** If the user wants specific imagery, call `search-media-library` to see what the tenant already has and reference those items. Do not re-add something the library already holds.
- **Share metadata** (optional, for social previews): share title, share description.

## Step 2 — Scaffold the entity

Call `create-landing-page` with:
- `name` — required
- `description` — if provided
- `page_title` — if provided

Capture the returned `id` and admin URL.

## Step 3 — Populate the body via `instruct-assistant`

This is the critical step — `create-landing-page` returns an **empty** page. Call:

```
instruct-assistant(
  entity_type="landing_page",
  entity_id=<id from step 2>,
  instruction="<detailed natural-language brief>"
)
```

`variant_id` is optional; leave it out and the first variant is used.

The instruction should be one block of text that lists every section to build, naming the block types explicitly. Example:

> Hero row with headline "Save the bees" and a short subheading. A paragraph explaining the campaign. A countdown timer to 2026-06-01 18:00. A signup form with fields: email (required), firstname, lastname, opt-in disclaimer with GDPR consent. A donation block with amounts 10€/25€/50€, anonymous donations allowed, tax-deduction text on. A progress bar sourced from DONATIONS with objective 100000 and postfix "€ raised". Share buttons for Facebook, WhatsApp, X. Use a green/blue color palette, large rounded buttons.

If `instruct-assistant` is not in the tool list, the tenant has not opted in to the AI assistant. Say so, and offer either the hosted-page route from step 0 or finishing the body in the Cambuildr editor.

## Step 4 — Wrap up

Report:
- The landing page admin URL (for editing/preview).
- Whether share metadata needs setting → if the user provided a share title or description, call `update-landing-page` with those.
- Whether to publish → ask the user; if yes, call `update-landing-page` with `is_published=true`.
- Offer further tweaks: another `instruct-assistant` call for content adjustments.

## What NOT to do

- Do not claim "the landing page is done" before step 3 runs successfully.
- Do not use `update-landing-page` to try to edit the body — that tool only changes metadata. Body edits go through `instruct-assistant`.
- Do not invent template IDs or block IDs; let the assistant agent pick them.
- Do not paste large HTML into `instruct-assistant`. Raw HTML belongs on a hosted page, via `set-hosted-landing-page-content`.
