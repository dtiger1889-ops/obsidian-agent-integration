---
created: 2026-07-01
updated: 2026-09-04
tags:
  - spec
  - obsidian
  - meta
---
# Capture → action-items loop — `/process-inbox` spec

> Goal: a note written on the phone (lands in `00 Inbox/` via Syncthing) becomes
> **durable reference filed into the PARA vault** + **to-dos turned into tracked
> action items**, with an agent doing the bookkeeping. Project/work items route
> directly to their known project; non-project filing choices wait in the vault's
> approval table. This is the "ingest" op of the Karpathy LLM-wiki model,
> extended with an action-item bridge. Companion doc:
> [integration-spec.md](integration-spec.md) (the two-lanes model).
>
> **Where this doc is superseded:** the task destination below was originally a
> separate task tool; it is now a Base inside the vault
> ([vault-bases.md](vault-bases.md)). The v1 approval gate — a chat table — is
> now a staging table ([approval-staging.md](approval-staging.md)). The pipeline
> shape, the classification rules, and the scope ladder are unchanged and are
> what this doc is still worth reading for.

## The pipeline (one processing pass)

```
00 Inbox/*.md + Clippings/*.md ──sweep──> parse ──classify──> review gate ──> execute ──> report
                                                                      │
                                                reference ──> PARA vault (dated, [[linked]], tagged)
                                                action     ──> task index (one note per item)
                                                personal   ──> flag only, never auto-file
                                                junk       ──> propose disposition, the user decides
```

### 1. Sweep
- Enumerate `00 Inbox/*.md` and `Clippings/*.md`. Web captures have their own
  lifecycle and visible queue; reviewed keepers are not reprocessed unless
  their instruction changed or their temporary value is being revisited. See
  [web-clippings-lifecycle.md](../lessons/web-clippings-lifecycle.md).
- **Skip** `*.sync-conflict-*` (flag, don't act — standing rule).
- **Skip** notes with `status: pinned` in frontmatter — pinned means "lives in the
  inbox on purpose" (e.g. a quick-reach command note). This is
  the opt-out lever: the user pins anything the processor should leave alone.

### 2. Parse
- YAML frontmatter observed in real inbox notes: `created`, `updated`, `due`,
  `tags`, `status`. `created` supplies the dated-provenance date when filing;
  `due` carries into the task item (and stays TaskNotes-compatible for the
  phone-reminders thread — don't strip it).
- Body may be **mixed** — the real `Todos.md` contains a wikilink, two tasks, and
  a complaint in five lines. Classification is per-chunk, not per-note.

### 3. Classify (per chunk)
| Class | Test | Destination |
|---|---|---|
| **Action item** | "do X" — a verb the user must perform, incl. `Dispatch:` items | task item (text, `due` from frontmatter/inline, context if obvious) |
| **Durable reference** | useful again later, answers a future situation | PARA file per retrieval-context rule; tag from the tag schema (never invent tags) |
| **Personal** (journal / venting / relationship / medical detail) | the personal-content territory in the tag schema | NEVER auto-file. Leave in inbox, flag to the user with a suggestion |
| **Ephemeral / junk** | stale one-liner, done already, fragment | propose leave-or-delete; the user decides (no unsolicited deletes — hard rule) |

Ambiguity rule: when a chunk could be task or reference, it's **both** — file the
reference AND push the task (e.g. "do X after shipping Y
calendar exporter" = a task with a dependency note).

### 4. Route or stage
Project/work items skip the approval gate: create the task-index item and route
the originating note to its project. Non-project items remain in the inbox with
an exact `proposed_dest`, approve/hold controls, and one plain-language agent
note. The approval table inside the vault is the gate; do not recreate it as a
chat transcript.

### 5. Execute (directly routed or approved items)
- **Reference →** append `## <Title> — <YYYY-MM-DD>` (date = note's `created`) to
  the target vault file, or create a new file when the situation is new (split,
  don't cram). Add `[[wikilinks]]` to related notes; tags per schema.
- **Tasks →** create one item note in the task index, carrying the text plus
  whatever metadata the capture supplied (due date and source context). The
  agent stamps tier and estimated context; the user does not maintain priority.
  Schema and conventions: [vault-bases.md](vault-bases.md).
- **Processed-note disposition →** move the source note to vault `Archive/`
  after every chunk is filed or explicitly closed.

### 6. Report
End-of-pass summary in chat: N notes swept, M filed, K tasks pushed, what was
skipped/flagged and why. A vault `log.md` (append-only, `## [date] ingest — …`)
is the Karpathy-op version — add it when the loop runs regularly, not v1.

## Worked example — three hypothetical inbox notes and how each routes
- **A mixed to-do note**: an actionable line ("do X after deploying Y") → task
  system. A dispatch-style line pointing at a `[[topic note]]` to investigate →
  task with context attached. A line that's feedback about a past assistant
  session → flag to the user, don't file (it's not vault reference material).
  A bare `[[wikilink]]` with no verb → context only, nothing to do.
- **A scratchpad tip** (a durable how-to the user jotted down) → reference note
  under the matching `Areas/` folder, tagged, dated section.
- **A pinned command note**: `status: pinned` → skipped, stays put.

## Skill packaging
- **The runtime's user-level Obsidian skill** (per integration-spec): the umbrella
  skill — orient via vault `HOME.md`, query/read, capture-to-inbox.
- **`/process-inbox`** = a mode/argument of that skill (`/obsidian process-inbox`
  or its own thin SKILL.md that shares the conventions file). Shared conventions
  (PARA map, dated provenance, tag pointer, personal-content gate) live ONCE —
  in vault `HOME.md` or a vault-level agent doc — and both read it.
- **`HOME.md` is a build prerequisite** (the processor's orientation input):
  single-screen PARA map + conventions. Build it first, same work session
  (~20 min, and it closes spec Phase 1 along with the project-side pointers).
  A worked copy: [HOME.example.md](HOME.example.md).

## Scope ladder (v1 → later)
1. **v1 (historical): propose-then-approve.** Every vault write and task push
   appeared in a chat table before execution.
2. **v2 (current): split by lane.** Project work routes directly because its
   destination is known; non-project choices remain gated in an approval Base.
3. v3: scheduled/dispatch runs + `log.md` + lint op (contradictions, orphans,
  stale claims) — the full self-maintaining wiki.

## Decisions (settled 2026-07-01 — model-recommended defaults, the user accepted)
1. **Processed-note disposition: move to vault `Archive/`.** Inbox stays clean;
   the original survives in case a filing went wrong. Not stamp-and-leave, not delete.
2. **Skill shape: ONE `/obsidian` skill** with process-inbox as a mode
   (`/obsidian process-inbox`), alongside query/read and capture.
3. **Conventions home: `HOME.md` carries both** — human folder map on top,
   agent rules (filing conventions, tag pointer, personal-content gate) below.
   No separate agent-instruction file of its own inside the vault.

## Settled operational choice
`status: pinned` is the opt-out marker: a pinned note deliberately remains where
it is and the inbox processor skips it.
