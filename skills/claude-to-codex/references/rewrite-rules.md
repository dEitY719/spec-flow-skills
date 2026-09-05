# spec-flow:claude-to-codex — Work-order rules

Turn the target phase document into a scope-bounded work order for Codex:
name the goal, the exact files in play, and where to stop. The generated
Codex documents must reduce ambiguity and avoid high-level narrative.

Preserve, unchanged, from the source phase document:
1. The original intent.
2. Important dependencies and preconditions.
3. File paths and architecture references.

For each generated Codex document:
- clearly state the goal
- define exact files to create or modify
- specify the implementation scope, scoped to the current Codex slice
  (not the full source checklist)
- exclude unrelated work
- provide ordered implementation steps
- pull hidden assumptions into an explicit "Assumptions / Notes" section
- if the source includes uncertain protocol details or unverified
  schemas, mark them clearly and instruct Codex to implement
  conservatively
- provide a concrete completion checklist
- include a Codex execution prompt block at the bottom
