<!--
Portions of this file are adapted from the "learning-output-style" plugin by Anthropic
(https://github.com/anthropics/claude-plugins-official/tree/main/plugins/learning-output-style),
licensed under the Apache License, Version 2.0. See the LICENSE and NOTICE files that ship with this
skill and at https://github.com/lucasddmc/depth-first-tutor.
Modified for depth-first-tutor in 2026: contributions are requested only inside a tutoring session,
for practice steps whose approach the learner already got right, and Insight blocks are used only as
feedback after the learner's attempt.
-->

# Practice in code: the TODO(human) spot

Use this for a practice step that involves code, after the learner's approach is right. The learner
writes the logic; you prepare the place for it.

## 1. Prepare the spot

Create or edit the file with:

- the surrounding context the code needs (imports, the caller, the data it receives)
- the function signature, with clear parameters and return type
- a comment saying what the function is for
- a `TODO(human)` marker, in the language's comment syntax, where the learner's code goes

Don't write the logic. The expected code is at most 15 lines.

This preparation is the scaffold: together with removing the marker in step 4, it is the only file
editing you do without being asked.

## 2. Ask for the contribution

Send a request in this shape, then stop and wait:

    ● Your turn

    Context: what is already in place, and why this piece matters.
    Your task: in <file>, write <the function or branch> at TODO(human).
    Guidance: the constraints and the trade-offs to weigh. Never the solution.

## 3. Review

When the learner says they're done, read the file. If there are tests, show the command that runs
them; the learner runs it.

- **Right:** give feedback in one Insight block with two or three points about their code: what works,
  what to watch, why.

      ★ Insight ─────────────────────────────────────
      - a point about the learner's code
      - another point about the learner's code
      ─────────────────────────────────────────────────

  The Insight comes only after the attempt. Before it, it would give the answer away.
- **Wrong:** show in at most 3 lines how what their code does differs from what it should do (the
  behaviour, not the corrected code) and ask one Socratic question that points at the error. They try
  again at the same spot. Give the full answer only after 2 failed attempts, and even then the learner
  types it in.

## 4. Close

- The `TODO(human)` marker must not survive: once the learner's code is in, remove the marker line if
  they left it. That counts as editing the scaffold.
- The `(practice)` node closes when the code runs or the tests pass. Record what the learner did, for
  example `→ wrote the lo/hi update; all 6 tests pass (2026-10-09)`.
- A `(practice)` node that needs several spots closes after the last one. If one spot teaches
  something on its own, give it its own `(practice)` child.

## When not to use a spot

Configuration, boilerplate and setup that teach nothing about the topic: show the exact content and the
learner pastes it, or, if they ask, you write it.
