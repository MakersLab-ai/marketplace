---
description: Start the 15-minute autonomous GROUNDCONTROL coding loop in this project.
---

# /gc-loop

Starts a recurring loop where every 15 minutes you check GROUNDCONTROL for assigned tasks, pick the highest priority, and ship a PR.

## Steps

1. **Pre-flight checks:**
   - Verify `.env` exists in the project root with `GC_API_KEY` set. If not, instruct the user to run `/gc-init` first and stop.
   - Call `gc_get_context` to confirm the key still works. If it fails, instruct the user to re-run `/gc-init` and stop.

2. **Start the loop** by invoking `/loop 15m /groundcontrol-for-claude-code:gc-check`.

   The fully-qualified command name is required: cron-fired prompts resolve against the global command registry and the un-namespaced `/gc-check` shorthand is not found there, so each scheduled tick would otherwise fail with `Unknown command: /gc-check`.

3. **Print:**
   ```
   GROUNDCONTROL loop started — /gc-check will run every 15 minutes.
   Stop it any time with /loop stop.
   First iteration runs now.
   ```
