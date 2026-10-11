# depth-first-tutor

A tutor mode for Claude that makes you do the thinking. You name a topic; Claude maps what you already
know, explores the prerequisites you're missing depth-first as a tree of questions, reads a reliable
source before teaching anything (or tells you plainly when it couldn't find one), asks you to try
before it shows solutions, and in code leaves `TODO(human)` spots for you to write.

It runs as a Claude Code plugin and as a skill you can upload to claude.ai.

## What a session looks like

1. You run `/depth-first-tutor:learn binary search`.
2. In its first message, every session, Claude tells you: if any concept it mentions stops you, even
   a little, say so. Then it restates the goal as a question and lists the concepts it depends on,
   and you mark each one: (K) I know it, (U) I've seen it but I'm unsure, (N) it's new to me.
3. For each concept you don't know, Claude explains it in a few lines and asks a question you can
   only answer by applying it. A concept you flag, or a prerequisite you need first, becomes a new
   branch, and the session goes down into it. Once it's settled, Claude brings back the explanation
   you were reading, in full, so you read it again with the missing piece in place.
4. Every time a node opens or closes, Claude redraws the tree:

   ```
   Goal: how does binary search find an item in O(log n)?
   Sources: 1 listed in the file

   ├── ✅ why must the array be sorted?               concept · U
   ├── 🎯 why does each step halve the search space?  concept · N  ← here
   │   ├── ○ what is the invariant between lo and hi?  concept
   │   ├── ■ why is log₂ n the number of halvings?     black-box
   │   └── ⏸ iterative or recursive version?           decision · later
   └── ○ implement it and pass the edge-case tests     practice ⇠ invariant

   ✅ closed  🎯 focus  ○ open  ⏸ deferred  ■ black-box
   ```

   `■` marks a concept you accepted as given for now, and `⇠` points to a prerequisite elsewhere in
   the tree.

5. Practice steps start with "how would you approach this?". In code, once your approach is right,
   Claude prepares the file and marks a `TODO(human)` spot, and you write the logic.
6. At the end you explain the whole thing back in 3–4 sentences, and Claude points out the gaps.

The tree is saved to `learning-trees/<topic>.md`, so the next session resumes where you stopped.
[examples/binary-search.md](examples/binary-search.md) shows the file format.

## Install

### Claude Code

```bash
claude plugin marketplace add lucasddmc/depth-first-tutor
claude plugin install depth-first-tutor@depth-first-tutor
```

Then run `/depth-first-tutor:learn <topic>` in a session, or ask "tutor me on binary search".

### claude.ai

Custom skills need a paid plan with code execution turned on.

1. Download `learn.zip` from the [latest release](https://github.com/lucasddmc/depth-first-tutor/releases/latest).
2. Upload it in **Customize > Skills** and turn it on.
3. Ask "tutor me on binary search", or on any topic. At the end, download the tree file, and attach
   it next time to resume.

### OpenCode

Copy the skill and the command into your global config:

```bash
mkdir -p ~/.config/opencode/skills ~/.config/opencode/commands
cp -r plugins/depth-first-tutor/skills/learn ~/.config/opencode/skills/
cp .opencode/commands/learn.md ~/.config/opencode/commands/
```

Then run `/learn binary search` in a session, or ask "tutor me on binary search".

### Other agents

`plugins/depth-first-tutor/skills/learn/` follows the
[Agent Skills specification](https://agentskills.io/specification). It has only been tested in
Claude Code, claude.ai, and OpenCode.

## Where trees are saved

By default, in `learning-trees/` inside the folder you're working in. To keep them all in one place,
add a line to the project's AGENTS.md (or `~/.claude/CLAUDE.md` for Claude):

```
depth-first-tutor trees: ~/notes/learning-trees
```

## Where the ideas come from

- **Nodes are questions,** and new questions come up while answering earlier ones: IBIS. Noble &
  Rittel (1988), *Issue-Based Information Systems for Design*, IURD Working Paper Series, UC Berkeley.
  https://escholarship.org/uc/item/4qt7f1vm
- **Prerequisites form a partial order,** so `depends:` edges make a DAG: Knowledge Space Theory.
  Doignon & Falmagne (1985), Spaces for the assessment of knowledge, *International Journal of
  Man-Machine Studies* 23(2), 175–196. doi:10.1016/S0020-7373(85)80031-6
- **Decision nodes** close with the option chosen and why, weighed against criteria: Questions,
  Options and Criteria. MacLean, Young, Bellotti & Moran (1991), Questions, options, and criteria:
  Elements of design space analysis, *Human–Computer Interaction* 6(3–4), 201–250.
- The `TODO(human)` mechanic and the Insight block format are adapted from Anthropic's
  `learning-output-style` plugin (Apache-2.0). See [NOTICE](NOTICE).

## Status

Built by one person and used across several subjects. It has not been evaluated with other learners,
so treat it as a method to try, not a proven result.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
