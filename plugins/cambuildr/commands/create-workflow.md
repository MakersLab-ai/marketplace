---
description: Create a Cambuildr workflow (Automation) — scaffold it, bind its start condition, write its graph, then activate it.
argument-hint: "[name]"
---

# /cambuildr:create-workflow

End-to-end workflow: scaffold an automation in Cambuildr, bind the event that enrolls people, write its graph, and activate it last.

The server ships this as the `build-workflow-automation` prompt. If the client can run it, prefer that — it is maintained alongside the tools. Use this command otherwise.

## Step 0 — Confirm this is a workflow

A workflow ("Automations" in the Cambuildr admin UI) is a multi-step graph: one enrolling event, then actions, waits and conditions.

- One email on one event, optionally delayed → that's a **triggered mail**. Use `/cambuildr:create-mail triggered`.
- A scheduled broadcast → that's a **campaign mail**. Use `/cambuildr:create-mail campaign`.
- "When someone signs up, wait three days, send a follow-up, and if they donated, tag them" → workflow. Continue here.

## Step 1 — Gather inputs

If the user passed a name as an argument, use it as the working title. Otherwise ask for one.

Then gather:
- **Description** (internal, optional).
- **Campaign** — should the workflow be filed under a campaign? Optional; omit to leave it standalone.
- **The enrolling event** — in plain language ("when someone donates", "when a person signs up on the spring campaign"). Do not ask for an action name; you resolve it in step 3.
- **The steps**, in order — which emails to send, which tags to attach, how long to wait between steps, what to branch on.
- **Re-enrollment** — may a person go through this more than once? `ONCE` (at most once, ever) or `EVERY_TIME` (may re-enroll after a previous run ended).

## Step 2 — Scaffold

```
create-workflow(name=<name>, description=<description>, campaign_id=<id or omitted>)
```

Capture the returned `id` and admin URL. The workflow is created **empty**: inactive, no graph, no start condition.

## Step 3 — Bind the start condition

A workflow has exactly one start condition, and `set-workflow-start-condition` replaces whatever is there.

Discover valid values first — the same catalog the triggered-mail tools use:

```
list-trigger-actions()                                  # dotted name.context keys by category
list-trigger-actions(action="<key>")                    # valid sources for that key
list-trigger-actions(action="<key>", source_id=<id>)    # valid classes / answers for that source
```

Then bind:

```
set-workflow-start-condition(
  id=<workflow id>,
  action="<name.context key>",
  source_id=<resolved source id>,
  class_id=<resolved class id>          # when the action has classes
)
```

Additional filters where the action supports them: `subclass_id` (event category for event-attendance actions), `product_ids` (Stripe purchase actions), and `value_min` / `value_max` for value-bearing actions such as donations. `allow_automation_origin` opts into enrolling on actions that an automation itself produced — leave it off unless the user wants cascades.

Set `is_internal_action=false` with `action_name` only when the user says the event is pushed in from another system.

## Step 4 — Read the building blocks

```
get-workflow(id=<workflow id>)
```

This returns the current graph, the start condition, and the building blocks a graph may reference: valid node kinds, the action types and their shapes, and the tenant's **real** automated-mail, tag and campaign ids. The `cambuildr://workflows/{workflow_id}/building-blocks` resource carries the same catalog.

Read this before writing a graph. A graph referencing invented ids is rejected.

## Step 5 — Write the graph

Two routes:

**Natural language (preferred when available):**
```
instruct-assistant(
  entity_type="workflow",
  entity_id=<workflow id>,
  instruction="<the steps in order, naming the mails, tags, waits and branch conditions>"
)
```
Do not pass `variant_id` — workflows have no variants, and supplying it is an error. If `instruct-assistant` is absent, the tenant has not opted in to the AI assistant; use the explicit route.

**Explicit graph:**
```
set-workflow-graph(id=<workflow id>, nodes=[…], edges=[…])
```

Rules that matter:
- **Full replace, never a diff.** Send every node and every edge each time, including the ones you are not changing. Base your write on what `get-workflow` returned.
- Node kinds are `START`, `ACTION`, `CONDITION`, `WAIT`. Exactly one `START` node.
- Only `CONDITION` nodes may have more than one outgoing edge; their out-edges are labelled `branch: "yes"` and/or `branch: "no"`, at most one of each and no other value. There is no `else` branch: leave a branch unwired and the run simply ends on that side. An edge that does not leave a `CONDITION` carries no branch.
- A wait is either a duration or an absolute date.
- Webhook URLs must be HTTPS on port 443 and resolve to a public address. A secret webhook header value comes back from `get-workflow` as a sentinel placeholder — send it back **unchanged** to keep the stored credential; anything else overwrites it.
- An invalid graph is rejected with error codes and nothing is saved. Fix and resend the whole graph.

## Step 6 — Set re-enrollment

```
update-workflow(id=<workflow id>, reenrollment="ONCE" | "EVERY_TIME")
```

## Step 7 — Activate, last

```
update-workflow(id=<workflow id>, active=true)
```

**If the graph contains a delete-person action, this returns a refusal saying review was requested.** That is the designed behaviour, not a failure: only Cambuildr can activate a workflow that deletes people, and the request has been passed to them. Tell the user their workflow is awaiting Cambuildr review and do not retry.

Otherwise confirm the workflow is live, name the event that enrolls people, and summarise the steps.

## Step 8 — Verify

Call `get-workflow` and confirm it reports the start condition, a published graph version, and `active: true`. Report the admin URL.

## What NOT to do

- Do not activate before the start condition and the graph are both in place. An active workflow with no graph does nothing; one with no start condition enrolls nobody.
- Do not send a partial graph to `set-workflow-graph`. It replaces everything.
- Do not invent mail, tag or campaign ids. Take them from `get-workflow`.
- Do not pass `variant_id` to `instruct-assistant` for a workflow.
- Do not retry activation of a delete-person workflow, and do not tell the user it is live.
- Do not use a workflow for what a single triggered mail does — one event, one email, optional delay is `/cambuildr:create-mail triggered`.
