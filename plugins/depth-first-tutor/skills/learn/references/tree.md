# The tree of questions

Every tutoring session keeps a tree in a file, even when the session looks too short to need one.
The file survives breaks between sessions and a compacted conversation; the chat history doesn't.

The design borrows from IBIS (issues, phrased as questions, organize the work, and new issues come up
while treating earlier ones), Knowledge Space Theory (prerequisites form a partial order, so the real
structure is a DAG) and QOC (decisions recorded with their options and the criteria behind the
choice).

## Where the file lives

1. If the learner attached a tree file, that file is the tree: resume from it and keep updating it.
2. If the user's CLAUDE.md or AGENTS.md has a line like `depth-first-tutor trees: <path>`, use that
   folder.
3. Otherwise use `learning-trees/` in the current working directory.
4. One file per topic, named `<topic-slug>.md` in kebab-case (`binary-search.md`).
5. To resume, list the folder and look for the same slug or a file whose `Goal:` asks the same thing.
   If you're not sure which file it is, ask.
6. If files don't outlive the conversation where you run (a chat sandbox, for example), keep the file
   there and offer it for download at the end of the session and whenever the learner stops. Tell
   them to attach it next time to resume.
7. If you can't write files at all, keep the tree in the conversation: the latest render is its state,
   and at the end you give the learner the full file content to save.

## File format

    # Learning tree: binary search

    Goal: how does binary search find an item in O(log n)?
    Sources:
    - Knuth, The Art of Computer Programming, Vol. 3: Sorting and Searching, 2nd ed. (1998), §6.2.1, Algorithm B · binary search on an ordered table
    Started: 2026-10-09
    Grammar: depth-first-tutor (references/tree.md)

    ## Tree

    - [CLOSED] (U) why must the array be sorted? → otherwise one comparison says nothing about which half holds the item (2026-10-09)
    - [FOCUS] (N) why does each step halve the search space?
        - [OPEN] what is the invariant between lo and hi? — alias: invariant
        - [CLOSED] (black-box) why is log₂ n the number of halvings? → accepted as given: halving n until 1 is left takes about log₂ n steps (2026-10-09)
        - [DEFERRED] (decision) iterative or recursive version? — reason: decide after the first version works
    - [OPEN] (practice) implement it and pass the edge-case tests — depends: invariant

Each source is a full reference or link, then `·` and what it supports. A tree with no source has
`Sources: ⚠️ ungrounded` instead of the list.

## Node grammar

One line per node:

    - [STATE] (type) (mark) question → answer (date) — alias: name — depends: name, name — reason: why

- **Indentation**: 4 spaces per level, showing where the question came up.
- **STATE**: `OPEN` (no answer yet) · `FOCUS` (being worked on now; at most one per tree) · `CLOSED`
  (answered or demonstrated; answer and date in the node) · `DEFERRED` (doesn't block the parent; the
  reason stays visible to future sessions).
- **type**, optional: none means a concept question, which closes with a written answer ·
  `(practice)` is a skill, which closes with a demonstration, and the node records what the learner
  did, not what they explained · `(decision)` is a choice with a real trade-off, which closes with the
  option chosen and why · `(black-box)` is a node closed by the stop rule.
- **mark**, optional: the learner's mapping mark: `(K)` know it, `(U)` seen it but unsure, `(N)` new.
  `(?)` is a mapping node the learner hasn't marked yet. `(practice)` nodes never carry a mark (they
  close only on a demonstration), and nodes created later, by rule 2, carry no
  mark. A `(K)` node enters already CLOSED with the answer "(K) at mapping", so reopening the topic
  needs no new mapping.
- **→ answer (date)**: one line, in the learner's words when possible. Short notes on attempts may
  follow, separated by `;`.
- **alias**: a short kebab-case name, only on nodes that another node depends on.
- **depends**: prerequisites that are not the parent, as aliases separated by commas
  (`— depends: probing, comparison`). Indentation records how the question was
  discovered; `depends:` records the real prerequisite. The graph is a DAG: never move a node to fix
  the hierarchy, add the edge instead.
- **reason**: why a node is DEFERRED.
- The node is a **question**, not a topic. "tensor product" never closes; "why do 2 qubits need 4
  amplitudes, not 2?" closes when the answer exists.
- No checkbox syntax (`- [ ]`): GitHub, Obsidian and task apps would read the nodes as to-dos.
- Objections and debates don't go in the tree.
- Questions, answers and reasons follow the learner's language. The grammar's keywords (the states,
  the types, the marks, `alias`, `depends`, `reason`, `Goal`, `Sources`, `Started`, `Grammar`) stay
  in English.

## Rules

1. **Mapping.** Each key concept becomes a child of the root, with its mark. Check the siblings:
   overlap becomes a merge or a `depends:` edge; a gap becomes a new node.
2. **New prerequisite.** A prerequisite the learner doesn't master that comes up in the middle of a
   node, or a concept the learner flags, becomes an OPEN child. Either of you may create it. When it
   has to be answered before the node can go on, it takes the FOCUS, and the node it came from goes
   back to OPEN until the focus returns to it.
3. **Closing a parent.** A parent closes only when every child is CLOSED or DEFERRED.
4. **Moving up.** When the FOCUS closes or is deferred, the focus moves to the parent (depth-first).
   When a top-level node closes, the focus moves to the next OPEN top-level node; when none is left,
   the session ends with the Feynman (rule 9).
5. **Full parent.** When the focus moves up, present the parent again in full: its explanation and its
   pending verification question, rewritten in the current message. Never repeat only the question and
   never ask the learner to scroll back to the earlier message. They read the parent before they had
   the child's piece, so that
   reading no longer counts. If the child changed how the parent should be understood, rewrite the
   parent with it.
6. **Stop rule.** Every concept has prerequisites all the way down to arithmetic; without a brake,
   depth-first takes over the session. Go down while the learner can't follow. Where they can **use
   the concept without the layer below**, close it as `(black-box)` with one line saying what is
   accepted as given. A black box is a legitimate close, not a debt, and it stays in the file so it can
   be reopened if not knowing that layer starts to hurt.
7. **You keep the file.** Update it on every state change, without asking. It is a record of the
   protocol, not learning content.
8. **Resume.** When a topic is reopened, read the tree before any mapping and propose resuming from the
   FOCUS node, if there is one, then from the OPEN and DEFERRED nodes.
9. **Root.** The root closes with the final Feynman: append ` → <the learner's explanation in one
   line> (date)` to the `Goal:` line.

## Render

Whenever a node opens, closes or is deferred, or the focus moves, update the file first and then show
the tree in a code block, rendered from the file. If several changes happen in one message, render
once, after the last one.

    Goal: how does binary search find an item in O(log n)?
    Sources: 1 listed in the file

    ├── ✅ why must the array be sorted?               concept · U
    ├── 🎯 why does each step halve the search space?  concept · N  ← here
    │   ├── ○ what is the invariant between lo and hi?  concept
    │   ├── ■ why is log₂ n the number of halvings?     black-box
    │   └── ⏸ iterative or recursive version?           decision · later
    └── ○ implement it and pass the edge-case tests     practice ⇠ invariant

    ✅ closed  🎯 focus  ○ open  ⏸ deferred  ■ black-box

- Each node shows its question, its type (`concept` when it has none) and its status. The mapping mark
  follows the type when there is one.
- Answers are not shown; they stay in the file.
- `■` replaces `✅` for a node closed as black-box. A deferred node shows its reason in a word or two.
  `depends:` shows as `⇠ <alias>, <alias>`. The focus ends with `← here`.
- A closed node whose whole subtree is closed collapses into one line: `✅ <question>  (+3 closed)`.
- With no sources, the second line reads `Sources: ⚠️ ungrounded`.
- When a node closes and the focus moves up, the render comes first and the full parent second.
