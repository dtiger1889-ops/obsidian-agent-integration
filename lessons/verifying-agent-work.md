# Checking an agent's work

Three verification failures inside one working day, in a system whose whole
premise is that an agent does the filing and a human spot-checks it. Written up
together because separately each reads as a dumb mistake, and together they make
one argument: **every layer of checking is itself something that can be wrong,
and the failure gets quieter the further up the stack it happens.**

1. A week-long pilot that passed because nothing happened.
2. A delegated agent's confident summary that did not match the file it
   described.
3. The two-minute check that caught that summary — which was itself broken, and
   briefly buried a real finding.

The third is the one worth the reading time, because it is the failure mode of
being diligent.

---

## 1. The pilot that could not have failed

**What was tried.** A change detector: the component that decides which notes an
agent needs to look at again, so a sweep doesn't re-read the whole vault every
run. Before wiring it into anything, it ran for a week of daily runs in log-only
mode — it recorded what it *would* have surfaced and changed nothing. The
go/no-go criterion was written down in advance, which is the part that was done
right: **the unseen count must trend to zero and must not ratchet up.**

Nine consecutive runs logged zero. On the face of it, a clean pass: no backlog,
no ratchet, nothing accumulating.

**What broke.** The pilot's scope was a single folder, and that folder's most
recent modification predated the pilot's start by four days. Nothing inside the
scope changed at any point during the window. Nine flat days did not mean
"detection is stable" — they meant "nothing happened." Zero was the arithmetic
of an empty input, and it was indistinguishable from the result the design was
hoping for.

**What it cost.** The evidence step that existed specifically to confirm the
design's central claim produced zero observations, and the pass was recorded
without anyone noticing that a flat line was the only outcome the setup could
produce. A detector was one step from being trusted on the strength of a
measurement that never measured anything.

**What replaced it.** A controlled test against a throwaway copy of the vault,
six cases, each with a required result decided before the run:

| Case | What is done to the copy | Required result |
|---|---|---|
| 1 | A new file appears | detect |
| 2 | An existing file's body is edited | detect |
| 3 | Only the `updated:` timestamp line changes, as an auto-formatter would do | **ignore** |
| 4 | The modification time is bumped, content byte-identical | **ignore** |
| 5 | Content changes but the modification time is forced 30 days into the past, as a phone-authored note arriving late over sync does | detect |
| 6 | Everything is acknowledged, then rescanned | zero |

Six for six, in ten minutes, with the input driven rather than waited for.

Two things about the shape of that suite matter more than the result:

- **Half the cases are must-ignore cases.** A detector that flags everything
  passes a detect-only suite perfectly. Cases 3 and 4 are not hypotheticals
  here: a linter rewriting `updated` on a note you merely opened is a
  documented failure in this vault
  ([vault-maintenance.md](../operations/vault-maintenance.md)), and a detector
  that treats it as a change re-surfaces half the vault every morning.
- **Case 5 is the one a quiet pilot can never reach.** A note written on a phone
  and carried over sync can arrive with a modification time well behind the
  clock. You will not observe that by watching; you have to stage it.

**The rule: a pilot over a quiet sample proves nothing.** Either drive the input
yourself, or widen the scope until the thing you are watching actually moves. A
monitoring window where the subject was inert is not weak evidence — it is no
evidence, and it is dangerous precisely because it produces a number.

---

## 2. The summary that did not match the artifact

**What was tried.** A delegated agent ran a research pass over a maintenance
question and reported back. Its headline finding: two duplicated notes had
drifted apart, one copy holding five entries the other lacked. That is exactly
the kind of finding the pass existed to surface, and it was written up as the
top line.

**What broke.** Opening both files and comparing them line by line took under a
minute. The bodies were byte-identical. The only difference was in frontmatter.
Nothing had drifted and nothing was missing.

**What it cost.** Nothing, because it was checked — but the cost it *would* have
carried is the reason to keep checking. A headline finding about lost content
sends the next session hunting for data that was never lost, and then
"reconciling" two files that already agree. The expensive part of a false
positive in a maintenance report is not the wasted hour; it is the edit somebody
makes to fix a problem that does not exist.

**What replaced it.** Two rules, the second easy to skip:

- **Check delegated work against the artifacts it claims to describe, never
  against its own summary.** A summary is the one part of the output that was
  generated rather than observed, and it is the only part most readers read. An
  agent's report is a claim about files; verification means opening the files.
- **Correct the record in the artifact the reader will actually open.** The
  wrong claim was not only in a chat reply — it was in a written finding that
  the next session would load. Correcting it in conversation and leaving the
  file alone means the wrong version is the durable one and the correction is
  the ephemeral one, which is exactly backwards.

---

## 3. The correction that was also wrong

**What was tried.** Immediately after that, the same agent's second claim was
spot-checked: that some number of tags were in use in the vault outside the
approved list. The spot-check took a couple of minutes, came back with nothing,
and the claim was written down as **"did not reproduce, treat as a lead."**
Careful wording, deliberately short of "false" — and still wrong.

**What broke.** The instrument. The check parsed the approved-tag list out of
the wrong part of the schema file and came away recognising four approved tags,
where the schema defines roughly thirty. Whatever that check was comparing, it
was not the vault's tags against the vault's allow-list, so nothing it said
about on-list versus off-list carried any information at all. Its silence was
not evidence of anything.

The same check, rebuilt properly inside the maintenance audit script a few days
later, confirmed a real problem on its first run: ten tags in use that are not
in the schema, one of them accounting for 54 uses.

**What it cost.** A true finding was written into the record as unreproduced. If
the audit had not been built shortly afterward, that downgrade would have been
the last word on it — a correct report from a delegated agent, discarded by a
broken check, with the discard preserved in writing and the finding not.

The deeper cost is the pattern. This did not happen because anyone was careless;
it happened *because* someone was being diligent. A verification result carries
authority — it closes the question — and a negative verification result reads as
reassurance, which is the one kind of output nobody re-examines.

**What replaced it.**

- **A cheap verification that contradicts a finding is itself a finding, and it
  needs verifying before you publish the correction.** The surprising result is
  the one that gets written down; make it the one that gets audited.
- **Calibrate the instrument on a known answer first.** Feed the checker one
  value you know is on the list and one you know is not. If it cannot tell them
  apart, its verdict on the real data is noise. This costs about thirty seconds
  and it is the entire fix.
- **A check that finds nothing should have to show what it *could* have
  found.** Have it print the size of the allow-list it loaded, the number of
  items it examined, the number it matched. Four-versus-thirty was visible in
  the check's own working set the whole time, and nothing was printing it.

---

## What the three have in common

**A check counts as evidence only if it could have come out the other way.** The
pilot ran against a folder where nothing could change. The spot-check ran with
an allow-list it had failed to load. Both produced a clean result, and neither
could have produced a dirty one. Before recording a pass, answer: *what exactly
would a failure have looked like here, and was that outcome reachable?*

**The artifact outranks the report about it.** This holds for a delegated
agent's summary, for a pilot's log, and for your own spot-check's output. Each
of those is a description of a thing; the thing is on disk and is cheap to open.

**Fix the record where it will be read.** A correction that only exists in a
conversation loses to the file every time.

**Build must-ignore cases, not just must-detect cases.** Anything that flags
changes, finds duplicates, or matches a schema can pass every positive test by
being indiscriminate. Half of a good suite is things it must stay quiet about.

**Suspect the verification layer specifically, because it is the layer nobody
verifies.** Work gets reviewed. Reviews do not.
