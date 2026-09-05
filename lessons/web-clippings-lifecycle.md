# Web clippings that do not become a second inbox

A web clipper solves capture and creates a second problem immediately: the
capture folder fills with pages whose status is unknowable. A clip may be new,
already reviewed, useful only until a task closes, worth keeping indefinitely,
ready to archive, or safe to delete. A folder name or a single `reviewed` tag
cannot express all of that honestly.

This is the lifecycle that survived real phone use. It combines four pieces:

1. frontmatter that separates review state, useful life, and disposition;
2. an Obsidian Base that makes every state visible and editable;
3. a preservation-first procedure for changing a Web Clipper full-settings
   export without losing unrelated settings; and
4. an explicit boundary between browser-extension settings, vault sync, and
   backup.

The raw settings export is deliberately not included. Full exports may carry
extension-owned identifiers, usage counters, template history, vault selectors,
and other user state. The reusable artifact is the procedure, not somebody
else's configuration.

---

## The model: four fields, four separate questions

Keep the clipper's source tag. Do not overload it with lifecycle state.

| Property | Question it answers | Allowed values |
|---|---|---|
| `tags` | What kind of note is this? | include the source tag `clippings` |
| `clip_status` | Has somebody made a decision about it? | `unreviewed` \| `reviewed` |
| `clip_reviewed` | When was that decision made? | `YYYY-MM-DD` \| blank |
| `clip_value` | How long is the source itself useful? | `temporary` \| `enduring` \| blank |
| `clip_disposition` | What should happen to the source note? | `keep` \| `archive` \| `delete` \| blank |

The capture contract is:

```yaml
clip_status: unreviewed
clip_reviewed:
clip_value:
clip_disposition:
tags:
  - clippings
```

Those are schema defaults, not a filled sample. A new clip is known to be
unreviewed and nothing else has been decided yet.

Review sets all four lifecycle fields together:

- `clip_status` becomes `reviewed`;
- `clip_reviewed` gets the review date;
- `clip_value` records whether the source is temporary or enduring; and
- `clip_disposition` records keep, archive, or delete.

This separation matters. `temporary` does not mean delete, and `enduring` does
not automatically mean keep. Useful life describes the source. Disposition
describes the next operation.

## The disposition rules

### Keep

Reviewed keepers stay in `Clippings/`. The folder becomes a source shelf as
well as a landing zone; the Base, not a folder move, separates reviewed material
from incoming work.

This is the natural merge of the "reviewed tag" and "reviewed archive folder"
ideas: use frontmatter for the decision, then leave useful sources where they
already live. A nested `Clippings/Archive/` adds a second archive policy without
adding information.

### Archive

Archive only after useful material has been extracted and every action created
from the clip has closed. Move the source into the vault's existing `Archive/`
using the same archive stamps and inbound-link checks as every other note.

`archive` is a queued disposition while the note remains visible in the Base.
It is not permission to hide a source that still explains open work.

### Delete

`delete` means candidate, not authorization. Leave the note visible until the
human explicitly approves that file's deletion. This preserves the distinction
between an agent's judgment and a destructive action.

---

## The Base: the review surface

Save the following as `Clippings base.base` at the vault root. The first view
is deliberately fail-closed: anything whose status is missing, blank, or not
exactly `reviewed` appears in **Needs review**. Older clips and broken templates
cannot silently bypass the queue.

```yaml
properties:
  title:
    displayName: Title
  clip_status:
    displayName: Review state
  clip_reviewed:
    displayName: Reviewed
  clip_value:
    displayName: Useful life
  clip_disposition:
    displayName: Disposition
  tags:
    displayName: Tags
  source:
    displayName: Source
  created:
    displayName: Captured
views:
  - type: table
    name: Needs review
    filters:
      and:
        - file.inFolder("Clippings")
        - clip_status != "reviewed"
    order:
      - file.name
      - title
      - source
      - tags
      - clip_status
      - clip_value
      - clip_disposition
      - created
    sort:
      - property: created
        direction: DESC
  - type: table
    name: Reviewed shelf
    filters:
      and:
        - file.inFolder("Clippings")
        - clip_status == "reviewed"
        - clip_disposition == "keep"
    groupBy:
      property: clip_value
      direction: ASC
    order:
      - file.name
      - title
      - clip_value
      - tags
      - clip_reviewed
      - source
    sort:
      - property: clip_reviewed
        direction: DESC
  - type: table
    name: Enduring library
    filters:
      and:
        - file.inFolder("Clippings")
        - clip_status == "reviewed"
        - clip_value == "enduring"
        - clip_disposition == "keep"
    order:
      - file.name
      - title
      - tags
      - clip_reviewed
      - source
    sort:
      - property: clip_reviewed
        direction: DESC
  - type: table
    name: Ready to archive
    filters:
      and:
        - file.inFolder("Clippings")
        - clip_status == "reviewed"
        - clip_disposition == "archive"
    order:
      - file.name
      - title
      - clip_value
      - tags
      - clip_reviewed
      - source
  - type: table
    name: Delete candidates
    filters:
      and:
        - file.inFolder("Clippings")
        - clip_status == "reviewed"
        - clip_disposition == "delete"
    order:
      - file.name
      - title
      - clip_value
      - tags
      - clip_reviewed
      - source
  - type: table
    name: All clips
    filters:
      and:
        - file.inFolder("Clippings")
    groupBy:
      property: clip_status
      direction: ASC
    order:
      - file.name
      - title
      - clip_status
      - clip_reviewed
      - clip_value
      - clip_disposition
      - tags
      - source
    sort:
      - property: created
        direction: DESC
```

Lead every view with `file.name`; that column is the link that opens the note.
The queue is only useful if it works on the phone, so verify view switching and
inline property editing there before relying on it.

---

## Safely add the fields to Web Clipper

Web Clipper's full export is a settings snapshot, not merely a template. The
failure mode is to rebuild a neat JSON file containing the template you care
about and accidentally discard every unrelated preference, empty section,
identifier, counter, and extension-owned field.

Use this preservation procedure instead.

The object names below describe the tested export shape. If a newer extension
emits a different schema, map that export before editing it; do not rename or
coerce unfamiliar fields to make them resemble this document.

### 1. Export the whole state

Use Web Clipper's **Export all settings** action. Treat that file as the current
source of truth. A prior project copy is not authoritative after somebody has
changed settings in the extension.

Hash the export and archive it untouched in a private location. Keep its
original filename. Never put the raw export in a public repository.

### 2. Make a literal copy

Copy the file byte-for-byte and edit only the copy. Do not construct a new JSON
object from remembered defaults. Avoid deserializing and reserializing the whole
document: even a semantically valid rewrite can reorder arrays, normalize empty
values, or omit fields the editing code does not know about.

### 3. Patch the existing template in place

Append four property definitions to the export's `property_types` registry, then
append the corresponding four property objects to the intended existing
template:

| Property | Type | Capture value |
|---|---|---|
| `clip_status` | text | `unreviewed` |
| `clip_reviewed` | date | blank |
| `clip_value` | text | blank |
| `clip_disposition` | text | blank |

Preserve the existing template's ID, name, path, behavior, note-name format,
content format, triggers, property order, and every existing property ID and
value. Give only the newly appended objects new, non-colliding IDs of the same
shape the export already uses.

Do not replace the template with a generated one unless replacing it is the
explicit goal.

### 4. Prove preservation semantically

Parse both files as JSON and flatten them into path-to-leaf-value maps. The
proposed file passes only when:

- every original path still exists;
- every original leaf value is unchanged;
- existing array members remain at the same indices;
- the only new leaf paths belong to the approved property-definition and
  template-property objects; and
- the only changed container facts are the expected array-length increases.

This gate catches the dangerous class of error: a file that parses and imports
successfully while silently resetting unrelated settings.

### 5. Hand off the exact validated copy

Keep one private project-owned current copy and place a byte-identical handoff
copy where the human expects uploads. Confirm their hashes match.

Import through the extension's **Import all settings** action. A template-only
import is a different operation and is not a substitute for preserving the
full export.

After the import succeeds and a real capture passes, retire the temporary
handoff. The next full export from the extension becomes the next baseline.

---

## Three transports that must not be conflated

### Browser-extension settings

The clipper's configuration belongs to the browser extension. A settings export
and **Import all settings** are its transfer mechanism. Do not assume extension
local storage is part of the Obsidian vault.

### Vault sync

Syncthing carries vault files between the desktop and phone. A clip created in
the synced `Clippings/` folder should arrive through that share. Android Debug
Bridge availability says only whether Android debugging is connected; it says
nothing about Syncthing peer state.

After scripted or bulk vault writes, force a Syncthing rescan if its file watcher
did not register the change. Verify folder completion in Syncthing itself rather
than inferring coverage from a running process.

### Backup

Two-way sync is not backup. A deletion or corruption can propagate to every
peer. Keep an independent versioned or one-way backup of the vault.

---

## End-to-end acceptance test

Do not stop at "the JSON imported."

1. Confirm the baseline and proposed settings files both parse.
2. Run the flattened-path preservation gate.
3. Import the full settings copy.
4. Capture one real page through the normal phone flow.
5. Confirm the note lands in `Clippings/` with `clip_status: unreviewed`, the
   three undecided lifecycle fields blank, and the `clippings` source tag.
6. Confirm the note appears in **Needs review**.
7. Review it and confirm it moves to exactly one disposition view.
8. Confirm the vault sync peer receives the file and no conflict copy appears.

That test validates the whole chain: extension settings, template output, vault
path, Base filters, and file transport. A successful import validates only the
first link.

## The lessons worth carrying elsewhere

- **Review state and storage location are different axes.** A reviewed keeper
  can stay in the capture folder when a queryable view separates it from new
  work.
- **Fail closed on missing metadata.** Old files and template failures belong in
  the review queue, not outside every view.
- **Preserve configuration wholesale, then patch narrowly.** Unknown fields are
  part of user state even when the current editor does not understand them.
- **An import surface defines the unit being replaced.** Template import and
  full-settings import are not interchangeable.
- **Test the real chain on the real device.** A valid JSON file is not evidence
  that capture, sync, and the review surface work together.
- **Name the transport before diagnosing it.** Browser settings, vault sync,
  Android debugging, and backup are separate mechanisms with separate evidence.
