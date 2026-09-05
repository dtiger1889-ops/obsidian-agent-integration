---
created: 2026-06-23
updated: 2026-09-04
tags:
  - spec
  - obsidian
  - meta
---
# Obsidian × agent projects — integration spec

> Goal: make the Obsidian vault a first-class, **searchable** reference layer for agent workspace projects, without blurring the line between *work* (projects) and *durable reference* (vault).

## The model — two systems, separate lanes

| | Agent projects | Obsidian vault |
|---|---|---|
| Path | `<WORKSPACE>/<project>/` | `<OBSIDIAN_VAULT>/` |
| Holds | active work: analysis, pipelines, artifacts | durable personal reference + writing |
| Driven by | agent + `CHECKPOINT.md` | human browsing, PARA |
| Backup | git (workspace repo) | Obsidian Sync |
| Agent can search it? | Yes, when the project is mounted | Yes, when the vault is mounted or bridged |

The vault being independently mountable is the key enabler: an agent can read it
without moving personal reference into the work repository. That is what makes a
read skill real rather than clever.

Integration is **one-way: projects point into the vault.** The project does the work; the vault holds the reference it draws on. New durable reference is *written to* the vault; work artifacts stay in the project. Don't merge the two.

## Domain mappings

Only some projects have a vault counterpart. The mapping is one project folder → one `Areas/` folder, and it exists only where a project genuinely draws on durable personal reference — a health-data project reading `Areas/Health/`, a job-search project reading `Areas/Career/`, a finance project reading `Areas/Finances/`.

Everything else has no vault side and gets **no pointer**. Purely personal vault areas (hobbies, relationships, home logistics, `Writing & Journal/`) have no project counterpart and are reached only via the skill.

Write the mapping down explicitly rather than letting sessions guess: a pointer that names the folder is what turns "the vault exists" into "this session will actually read it."

## Components

### 1. Vault `HOME.md` index
A single-screen map at the vault root. Contains:
- The PARA structure, one line per Area/Resource folder (what's in it, when you'd open it).
- The vault conventions (below).

It's the cheap orientation entry point — read HOME → drill to the specific note (progressive disclosure). Doubles as a personal dashboard inside Obsidian.

### 2. CHECKPOINT pointer convention
Each mapped project's `CHECKPOINT.md` gets one block:

```
## Obsidian
Domain reference: ~/Documents/Obsidian Vault/Areas/<domain>/
(<the two or three notes most likely to matter>). Read the
specific note when the task needs it; don't load the folder.
```

Lives in the startup read path, so any session in that project learns the pointer automatically. Zero new machinery — highest leverage-to-effort piece.

### 3. `/obsidian` skill (user-level)
Lives in the runtime's user-level skills directory so it is available in every project and standalone. Capabilities, phased by risk:

- **Query / read** (safe core): orient via HOME, Grep the vault, read the relevant note, answer. the pattern: one question, one note, answered from any session.
- **Capture**: drop a dated note into `00 Inbox/` (the existing Obsidian inbox; sort later).
- **Process inbox**: classify by chunk, directly route known project work, and stage ambiguous or personal filing choices.
- **Sprint notes**: treat non-empty `note` fields as queued human instructions, reply, then clear only what was handled.
- **Work the agent's plate**: route assigned items by their estimated context size while leaving human-gated work alone.

The skill encodes (or reads from HOME): vault root, PARA map, the conventions below.

## Conventions (rules that writes + the skill follow)
- **Dated provenance** — every consolidated entry keeps `## <Title> — <YYYY-MM-DD>` (created date). The date is the spine.
- **Retrieval-context organization (why / when / what / who)** — a file answers ONE situation. Notes sharing a tag but used in different moments go in separate files. Don't cram; don't hedge "borderline" — if the situation differs, split.
- **Personal content is the user's call** — journal / relationship / rage / personal-medical: never auto-write or restructure; capture to Inbox or ask.
- **Skip sync-conflicts** — ignore `*.sync-conflict-*` files on read; flag, don't act on them.
- **Don't load wholesale** — read the specific note, never a whole folder, into context.

## Historical build order
1. **Phase 1 (~20 min, low-risk):** `HOME.md` + one pointer per mapped project. Immediately makes the vault discoverable from those projects.
2. **Phase 2:** `/obsidian` skill, read/query only.
3. **Phase 3:** capture-to-Inbox.
4. **Phase 4:** routed writes (gated for personal content).

## Caveats
- ~~**Hosted sessions can't see the vault** — it is local; they will not have it mounted.~~ **No longer universally true**: some connected desktop runtimes expose a device bridge that reaches local files from a hosted session. Re-check the runtime rather than assuming. See [cowork-deployment-lessons.md](../operations/cowork-deployment-lessons.md).
- **Backup is separate** — the vault and the code workspace are backed up by different mechanisms. Both covered, different domains; don't assume one covers the other.

## Decisions from the original build
- How far the skill should go: read-only / +capture / +routed writes. *(Resolved: query, capture, process-inbox, sprint-notes, and work-the-agent-plate — see [SYSTEM-OVERVIEW.md](../SYSTEM-OVERVIEW.md) chunk 7.)*
- Whether conventions live in `HOME.md`, or a dedicated agent-rules file with HOME as the human index. *(Resolved: `HOME.md` carries both — [HOME.example.md](HOME.example.md).)*
- Which projects beyond the first few should map.
- Minor: stray notes at the vault root → `00 Inbox/` or file them.
