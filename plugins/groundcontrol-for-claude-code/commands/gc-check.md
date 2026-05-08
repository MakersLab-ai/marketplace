---
description: Run one iteration of the GROUNDCONTROL coding agent — react to changes, pick a task, ship a PR.
---

# /gc-check

One iteration of the autonomous coding agent. Designed to be invoked by `/loop`, but also usable standalone if you want to nudge the agent to check now.

Follow the `groundcontrol-coding` skill end-to-end:

1. Read cursor from `.gc-state.json`.
2. `gc_get_changes(since=<cursor>)` and react.
3. `gc_list_tasks` (scoped by `GC_INITIATIVE_ID` if set).
4. Pick highest-priority eligible task.
5. Implement → branch → commit → push → PR → closing comment → status `done`.
6. On blocker: stay `in_progress`, post comment, move to next task.
7. Persist new cursor.

This is **non-interactive**. Do not prompt the user. Communicate via task comments.
