# Sprints: the life of an action item, and the decision board on top of it

[vault-bases.md](vault-bases.md) has the Sprints Base itself — the frontmatter
schema, the `.base` YAML, the eight views. This doc is the other half: what
happens to a row **over time**. Where rows come from, what the agent stamps on
them, the ten-minute weekly ritual on the human side, how the agent drains its
own plate, how a row closes, and the newest piece — a **decision board** that
sits on top of the Base so the choices that are genuinely the human's to make
stop rotting in files nobody opens.

Everything below is running daily. The failure record at the end is the part
worth reading twice: the board took six wrong builds before the right one.

> Naming, as in the rest of this repo: `agent` is the frontmatter field where
> the live system uses a model nickname; "the owner" is the human. Substitute
> your own project slugs and vault paths.

---

## 1. Where rows come from

**One note per action item**, in `Projects/Sprints/`. The filename is the
stable identity (other notes `[[link]]` to it); the `summary` property is the
sentence that changes as the item evolves. Rows arrive by four routes:

| Route | What creates the row | Asked about first? |
|---|---|---|
| **Inbox sweep** | A phone capture with a task chunk in it. The sweep makes the row and moves the originating note into `Projects/`. | No — project work skips the approval gate ([approval-staging.md](approval-staging.md)). |
| **A project session's research** | A finding in a project's `research/` folder that recommends something. See the three-bucket rule below. | No, but it is *enforced*: the project's checkpoint verifier refuses to close while a filed recommendation has no row. |
| **Idea triage** | An idea in the triage queue whose `write_spec` box got ticked and whose spec survived. | The tick was the approval. |
| **The owner, directly** | A note created by hand in the folder, or a line in the Base. | — |

**The three-bucket rule for research files** exists because of a specific
night. An agent run drained thirteen rows off its own plate, filed seven
research reports carrying a dated "model recommendation" line each, closed the
rows that had pointed at them — and nothing surfaced the seven recommendations
to the owner. His question was the whole design brief: *"How am I supposed to
know what to review? Who's tracking that? It's filed — how do I know it's filed
later?"* A workspace scan the same night found thirty older research files in
the same state.

So a file in a project's `research/` folder is exactly one of three things:

1. **Consumed** — acted on or decided. It moves to `archive/research/` with a
   pointer from whatever consumed it (the decision record, the rule, the
   changelog entry). The decisions folder holds the *decision*, never the
   research that fed it.
2. **An action candidate** — it recommends something a human must decide or an
   agent must build. It is **not tracked until it is a Sprint row.** The file
   stays in `research/` until the row closes, then follows rule 1.
3. **Nice to have** — reference that may never be acted on. That is a vault
   item, filed into the reference tree, with the project copy archived.

Rule 2 is mechanical: at every checkpoint close, the verifier lists any
research file newer than the checkpoint's previous stamp that carries a dated
`model recommendation -- YYYY-MM-DD` attribution and is named by no Sprint row
for that project and no owner-gated open thread — and refuses the close. The
attribution form matters: the first cut matched the bare phrase and flagged its
own dry-run report, which merely quoted it. Prose mentions are not
recommendations.

---

## 2. What the agent stamps at intake

Every signal on a row is agent-stamped or computed. The one field that ever
needed the human to fill it in (`priority`) was blank on a third of the rows
and carried no signal on the rest; it was retired. What the agent writes:

- **`summary`** — one sentence, verb first, the first physical step. Fifteen
  minutes or less where the item allows it. History and options go in `reply`
  or the source note, never the summary.
- **`project`** — the workspace project whose *session* should execute the
  remaining work. Routed by execution owner, not by deliverable type, not by
  which folder holds a supporting file, not by topic. `personal` / `home` /
  `work` only when no project owns the action.
- **`project_assignment_log`** — an append-only ledger: date, which agent or
  runtime made the call, the project, and a plain-language reason. A wrong
  routing is *corrected by appending*, never by erasing the bad entry; an
  unknown router is written as `agent unknown`, never guessed. It lives on the
  temporary Sprint note, not on the permanent source note.
- **`complexity`** — `quick | moderate | heavy`.
- **`tier`** — `now | soon | someday`, by a dumb explainable heuristic: `now`
  is real money, health, a deadline, or a one-word unblock of already-built
  work; `someday` is a tool trial or a parked decision with no external
  pressure; everything else is `soon`. The owner vetoes in `note`, and a veto
  sticks until he changes it. Tiering never deletes anything; `someday` is a
  parking lot with its own tab.
- **`agent`** — `true` means *on the agent's plate*: assigned, not merely
  delegable. Work that needs a human's green light stays `false`, with the ask
  written once in `reply`. Every flip gets a dated, attributed reply.
- **`est_context`** — agent rows only: `small | medium | large`, the context a
  session needs to *finish* it (roughly: under a small budget inline / one
  project session / multi-session or fan-out). Not a time estimate.
- **`source`** — a wikilink back to the origin note. Multiple origins are a
  YAML list, one link per line; a scalar with two links parses as one malformed
  target and spawns a junk note.
- **`done: false`**, and the notes lane pair `note` / `reply`, empty.

---

## 3. The weekly ten minutes (the owner's side)

This is the whole ritual, and it was designed to fit in ten minutes on a phone:

1. Open the **Now** tab. It holds at most three picks. Do one, or veto it in the
   Note column.
2. Glance at **Decide**. Every row there opens its `reply` with the agent's
   suggested default and a decide-by date, so each one is a yes/no rather than
   an essay. Answer one.
3. Type anything else into the Note column on any row, on any tab.
4. Say **"act on my sprint notes."**

When a usage window on the agent's side resets, open the **Agent's plate** tab
and say **"work the plate"**, optionally with a size (`small` / `medium` /
`large`). The tab is grouped by `est_context`, so the budget you have maps onto
the rows you can afford.

Two things make this survivable. The Note column shows on every tab you
actually read line by line, so annotating never means switching views. And
typing a note **never triggers anything by itself** — the queue waits for you
to hand it over.

---

## 4. The notes lane, as a protocol

`note` is the human's voice; `reply` is the agent's. Four lines of YAML, and the
highest-leverage piece of the whole system.

**Any run that touches the Base at all drains the non-empty `note` rows first**,
before doing its own job — a work-the-plate run, an inbox sweep, a Now refresh.
The owner's line-by-line pass routinely retargets, deprioritises, or kills rows
the run would otherwise have executed. Reading a note *after* working the row
is how you end up doing something he just cancelled.

1. Collect every row with a non-empty `note`. Read the row in full, and its
   `source` when the note needs that context.
2. Act on each note per what it actually says. A question → the answer goes in
   `reply`. A task → do it, routed to the owning project under that project's
   own rules. Metadata → edit the frontmatter. "Drop this" / "done" → record
   completion in the linked note or project record *first*, then delete the row.
   A step the agent structurally cannot do (an auth flow, a device in hand, a
   UI-only click) is **tabled and said so in `reply`**, not attempted — one
   cheap probe to confirm the gate is fine; a retry ladder is not.
3. Close the exchange: write `reply` as one short dated line, then **clear
   `note`**. The reply is the receipt; the cleared note is what empties the
   queue. Never clear a note you did not act on; if one cannot be acted on this
   run, leave it and say why in the summary.
4. Unprompted replies are allowed from any session that learns something about
   a row (it shipped, its premise died) — but nothing ever writes into `note`.

**Reply voice is the rule that took longest to stick.** The owner reads `reply`
cold, on a phone, weeks later. So a reply is plain English with no workspace
shorthand: no field or enum names, no view names used as labels, no
file-and-line or script names, no status codes, no spec numbering. Keep a path
or a UI name only when it is the literal thing his next step needs. The test is
not "is this a code word" but **"can a stranger act on this without opening
another file"** — ordinary-looking English whose meaning lives in a different
document fails it just the same. A recommendation reads `suggest: …`, never
dressed as something that happened.

---

## 5. Working the agent's plate

The command that turns a usage-window reset into finished rows.

0. **Drain the note queue first** (section 4).
1. **Collect** every row with `agent: true` and `done != true`, grouped by
   `est_context`. With a size given, take that group only; with none, take
   `small` first and stop before `large` unless told otherwise. Skip rows whose
   `status` is `blocked` or whose `reply` shows a human gate.
2. **Mark the burn.** Before the first worker, and before and after each one,
   the run appends a usage mark (tokens, duration, rows, which provider) to a
   limits ledger, so the batch gets a cost line. The marks are written even when
   the live percentages are unavailable — the tokens still count either way.
3. **Orient each row as its own job.** The row's `project` names the executor;
   each worker reads *that project's* instruction and checkpoint files plus the
   row's `source` note, never this vault's manual. Routing follows the workspace
   cost gate: `small` rows run inline or on cheap parallel workers; `medium`
   rows get one worker each (a cheap model for mechanical work, the taste-tier
   model for anything a person will read); `large` rows are **not** fanned out —
   they are reported as needing their own session and skipped.
4. **Close each row the normal way:** completion recorded in the owning
   project's checkpoint or the source note, a dated `reply` on the row, then
   `done: true` (the next sweep deletes it). A row that stopped gets a dated
   `reply` naming exactly what stopped it, `status: blocked`, and `agent: false`
   if it now needs the human.
5. **Summary in chat:** rows finished / blocked / skipped, one line each, plus
   the batch cost line.

This mode is also where the three-bucket rule earns its keep: the run that
files research *while* closing rows is exactly the run that used to strand
recommendations. The verifier at the next checkpoint close catches it now.

---

## 6. Sweep maintenance

Run at the end of every sprint-notes run and every inbox sweep:

- **Tier re-stamp** by the same heuristic as intake; vetoes in `note` stick.
- **Staleness check, never auto-demote.** For each owner-owned row untouched
  for 30+ days, ask *one* question: did something happen that makes this
  pointless now? Check the source note, the owning project's checkpoint,
  whether it shipped or got decided elsewhere. Write the verdict as a dated
  reply — `still live: <why>` / `looks pointless now: <evidence>, suggest close`
  / `already done via X, suggest close`. The tier does not move on the agent's
  say-so; the owner closes or re-tiers. A row with a fresh verdict is left
  alone for another 30 days. (The owner's exact position: he does not like
  auto-demote; he likes auto-*check* for staleness.)
- **Suggested default on every Decide row.** Any owner-owned row blocked on his
  own decision opens its `reply` with `<date> -- Suggested default (agent):
  <the option>. Decide by <about 30 days out>; silence keeps the item open,
  nothing runs on its own.` The default is never executed without his go.
- **Done sweep.** `done: true` is the explicit close signal (legacy
  `status: done` is treated identically, and every view hides both). For each
  closed row: write the completion into the origin note or project record,
  sever any live vault links to the row (an archived or deleted note with a live
  inbound link becomes a grey node that re-spawns a junk note), then delete the
  row — one delete per file with its literal path, never a multi-path command.
  If completion cannot be recorded safely, leave the row checked and report
  what blocked it.
- **`status: verify` splits by who can check.** Machine-checkable → the agent
  verifies during the sweep, writes the evidence, deletes the row.
  Human-gated → it stays in his queue as a one-line confirm, never attempted.
- **Now-3 refill.** Keep at most three rows stamped `next: true` with a
  `picked` date, drawn only from the owner's queue, by the dumb heuristic (one
  quick unblocked + one moderate/heavy + the cheapest highest-leverage unblock —
  a "say go" that frees a built pipeline beats a random third). Picks are
  **sticky**: one survives until its row is deleted or vetoed; displacing a live
  pick needs a stated reason in `reply`.
- **Heartbeat.** The landing note that embeds the Base carries a
  `**Last swept:** <date>, <count> rows, <one clause>` line. A stale date is
  the only visible signal that the automation quietly died.

---

## 7. Decide rows: what makes something a decision

The **Decide** tab is every owner-owned row with `status: blocked`. That is a
filter, not a definition, and the gap between the two is where the decision
board came from.

A row is blocked because *something* is waiting on the human. Often that
something is not a decision at all: run this command, paste that key, click the
approve button, spend the tokens when you feel like it. Putting those in front
of him as "decisions" trains him to skim the list, and then the real forks get
skimmed too.

A candidate is a **decision the owner must make** only if all three hold:

1. **A genuine fork** — materially different options with different outcomes.
2. **It needs his judgment specifically** — taste, strategy, product intent,
   risk appetite. An agent cannot settle it with a recommendation and just do it.
3. **It is live now** — not parked behind a precondition whose answer is
   already obvious.

It is **not** a decision, and gets discarded with the reason named, if it is:

- the project's normal improve-loop ("fold in whatever makes it better" — that
  is the job, not a choice);
- already decided, or obvious to him (a stale "idea to explore" thread does not
  reopen something he has stated three times);
- scheduling, opportunity cost, token budget ("when do I spend the time on this
  obviously-fine thing");
- verification or execution ("prove it works", "fire the staged step");
- mechanical with one right answer (a session can just do it);
- deferred behind an obvious precondition (a network that needs users who do
  not exist yet).

Signals from the data help but none is sufficient alone: a blocked, owner-owned
row whose `reply` opens with a suggested default is *usually* a decision; an
owner-gated open thread whose text is "run X / paste Y" is execution; a "go /
no-go" thread is a decision only if the go is a real fork (build A vs B vs not
at all), not a rubber stamp on obvious work. And a spec existing is not evidence
the owner wants the thing in it.

Worked classification from the session that produced this test — use it as a
fixture:

| Candidate | Verdict | Why |
|---|---|---|
| Which cross-domain reuse ideas to pursue | not a decision | the normal improve-loop |
| Design of an integrity audit | decided in one line | the owner picked "narrow checks first" in chat; no board needed |
| Whether to invest in an interactive-page system | already decided | long-standing stated intent |
| Launch the next public wave, or hold | not a decision | token-spend scheduling |
| Let users send sessions back for analytics | not a live decision | he wants it → just build it |
| A community network of contributors | not live now | deferred behind an absent user base |
| A contributor pull-request skill | never wanted | lifted from a drafted spec he had not adopted |

Net result for that project, that day: **an empty board**. Empty is a correct,
valid output. The skill must never manufacture a decision to fill space.

---

## 8. The decision board

A private, single-page board of **only** the choices that pass section 7's
test for one project, each with its options and, per option, why you'd pick
it, what it costs, and what it unblocks. Built on demand ("show me my
decisions" / a `/decisions` command), one project at a time, redeployed to the
**same URL** each time so the page is a stable bookmark.

### What it is built from

Two sources, both mechanical: the project's checkpoint file's open-threads
bullets (with their owner tags), and every Sprint row whose `project` matches
the slug and is not done. A small collector emits them as JSON and never
classifies. The Sprints Base stays the **feed** — a filed recommendation
reaches the board only by first becoming a row (section 1) — and the board is
the readable layer over the Decide rows, not a replacement for the tab.

### The order of operations is the design

1. **Read back** what the owner did on the last board (below) before anything
   else.
2. **Collect** candidates.
3. **Classify every one** with section 7's test and **print the verdict table
   before building** — candidate, verdict, one-line reason. The owner vetoes in
   chat; the struck ones come off and the build continues. This is the step the
   failed builds skipped.
4. **Write each survivor plainly.** For every decision:
   - `title` — the fork as a question, no field names or workspace shorthand;
   - `background` — two to four sentences giving the context the owner does
     *not* have while reading cold: what the thing is, where it came from (the
     clip, the incident, the earlier row), what was found, what the options are
     about. A title plus options is not a decision; the background is what
     makes it one;
   - `why_now` — one sentence;
   - `sources` — labelled paths: the research file it came from, the clip or
     note that started it, the Sprint row — so he can go deeper without asking;
   - two to four `options`, each with `choose_if`, `cost`, `unblocks` —
     concrete, no workflow-state labels, no invented taxonomy;
   - `default` — the option the row's suggested-default line names.
   - The discards go on the page too, as a **left off** list with each verdict,
     so a misclassification is visible without him having to ask.
5. **Build and publish.** The data is written to a JSON file in the project's
   outputs folder, rendered into a static page from a template, and published
   through the agent runtime's hosted-page feature (here: a Claude Code
   artifact declaring a small key-value store). A registry file maps project
   slug → page URL; a later run passes the URL so the same page is redeployed
   and its saved state survives.
6. **Report in at most six lines**: the URL, how many decisions, their titles,
   how many were left off, and anything from step 1 that got applied.

### Capture: the page writes, the next session reads

Every option has a **Pick this** button. Every decision also has a note field
with its own **Save note** button. Both write a small record to the page's
store — `{decision, option, note, at}` — and the page shows the state on the
card: *picked*, *note saved, no pick*, or *open*.

The next run, and any checkpoint close in that project, reads those records
back before doing anything else:

- **A pick** → a dated `reply` on the matching Sprint row ("you picked X on
  <date>: <note>"), `done: true` when the pick closes the row, or `status:
  open` + `agent: true` when the pick is "go build it"; the checkpoint thread
  updated if one exists; one line in chat saying what he picked and what that
  set in motion.
- **A note with no pick** → treated as a **question**, not a decision. It is
  answered in a dated `reply` on the row (and in chat), the row stays open, and
  when the board is rebuilt the answer is carried into that decision's
  `background` so he sees it on the page.

Nothing is written to disk until he clicks something; and the Save-note button
exists precisely so that "I have a question about this one" is a click, not a
gap.

### What it is not

It is not the open-threads list (that is the checkpoint), not a to-do list
(that is the Base), and not a status dashboard. Nothing else goes on it. If
nothing passes the test, the run says so in one line and — if a page already
exists for the project — republishes it empty, so the page is honest.

---

## 9. The failure record

The board took six wrong builds in one session before the definition in
section 7 existed, then two more corrections after the first correct one. Each
one is a rule now.

**Failure 1 — owed work mistaken for decisions.** The first build pulled
fourteen items from the checkpoint's open threads and anything tagged for the
owner, and grouped them by workflow state (blocked-on-you / ready-to-build /
verify / deferred). Most were mechanical work or verification. The owner's
reaction, paraphrased: *I only need the things I have to decide. I do not care
whether the gate is mechanical. Why would I need to know anything else?* An
owner tag means "waiting on the owner for something" — usually firing a step or
spending time, not deciding.

**Failure 2 — a spec's framing imported as the owner's intent.** The board
headlined a "contributor pull-request skill" lifted from a drafted spec. He had
never wanted it; the two things he *did* want were missing entirely. A spec
existing for X is not evidence anyone wants X. Drafted proposals are
proposals.

**Failure 3 — asking the owner to configure abstractions.** A prompt asked him
to pick which "trade-off lenses" (effort, risk, value, verification cost) the
options should be compared on. He could not tell what the options meant. The
board's entire job is to *do* the trade-off work and present, per option, the
plain reason to pick it. Asking him to choose framework dimensions handed the
work back in jargon.

**Failure 4 — the normal improve-loop presented as a menu.** "Which cross-game
reuse ideas do you pursue?" The owner: the whole point of the project is that
when something makes it better, it goes in; there is nothing to pick. A list of
improvement avenues is a to-do list dressed as a choice.

**Failure 5 — settled questions reopened.** "Do you invest in the interactive
system?" — a thing he had stated repeatedly. The build read a thread's stale
"idea to explore" status instead of his stated position.

**Failure 6 — scheduling presented as a fork.** "Approve the next public wave,
or hold?" His answer: holding is not a decision, it is a matter of when to
spend the tokens. No fork, no judgment, just budget timing.

**The meta-failure — whittling instead of defining.** Five rounds of removing
one item at a time, each removal teaching the criterion the build should have
started with. The fix is structural: classify first, print the verdicts, build
only what passes.

**Failure 7 — the first correct board shipped without context.** Eight
decisions, every one of them a real fork, and one of them read: *"Do the two
token-saving habits become standing rules? Out of three saved threads, only
these two change anything for a one-hour cache."* The owner: *I have zero
context for what these mean. That means the artifact is useless.* The
`background` and `sources` fields exist because of that sentence, and the
skill now refuses to call a title-plus-options a decision.

**Failure 8 — no way to ask a question.** The first page could only save a
pick. A question about a decision, with no pick, wrote nothing to disk — which
is a gap in a system whose whole promise is "nothing gets lost." The Save-note
button and the note-only read-back (a question is answered, the row stays open,
the answer lands in the background) closed it the same night.

---

## 10. Three surfaces, one row

| Surface | Owns | Who writes it | What flows out |
|---|---|---|---|
| **Sprint row** (the Base) | The item's existence, routing, tier, size, the notes lane | Agent at intake and on sweeps; the owner in `note` and `done` | Closes into the origin note or project record, then is deleted |
| **Checkpoint open thread** | The project-side view of the same work, with a gate tag and a complexity tag | The project session at close | Gets a dated line when a board pick lands |
| **Decision board** | Only the forks that pass the test, with options written out | The skill, from the two above | Picks and questions, read back into `reply` on the row |

The row is the unit. The thread is where a project session sees it. The board
is where the human decides it. Nothing is tracked until it is a row — that is
the sentence the whole system reduces to.
