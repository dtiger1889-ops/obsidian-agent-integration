# Keep workspace browsing out of personal-vault startup

## What failed

A desktop vault exposed the agent workspace through a directory junction. This
made project notes convenient to browse, but also exposed the workspace's other
files and directories to Obsidian. Filtering search results did not establish
that enumeration or plugin startup would skip those entries.

The initial suspicion was a task plugin. Controlled comparisons did not support
blaming it alone: an ordinary copy of the workspace Markdown loaded quickly with
the same plugins, while the real broad workspace remained slower with a fresh
cache. Desktop startup improved from roughly nine seconds to about 1.3 seconds
after workspace access moved into a separate, on-demand vault.

An earlier attempt to detach the junction and reopen the existing vault hung.
The cause of that hang was not established. The successful migration preserved
profile and settings rollback material, cleared only the derived file/metadata
cache, and retained recovery and sync databases. This is an incident record,
not a recommendation to clear application data or delete arbitrary databases.

## The resulting separation

The personal vault contains durable notes. A separate desktop vault provides a
junction into the real workspace; a separate phone vault contains the synced
workspace copy. The agent still reads personal notes directly from the filesystem.
Moving the viewing surface does not require moving the real desktop projects.

Cross-vault dashboard links must be updated to the new vault or absolute phone
path. Return to the personal vault after browsing projects so the next launch
does not restore the larger workspace. Never recursively delete through a
workspace junction: it leads into the real working files.

## The phone path and sync-direction traps

The regular Syncthing folder editor displayed a locked path field. The editable
field was in the Web GUI's global Advanced Configuration, under the existing
folder entry. The migration sequence was to pause that share, move its files,
change its local path while preserving the folder ID and other settings, then
resume. The separate parent folder also had to be opened as a vault in Obsidian.
Changing a path in Syncthing does not itself move files or register a vault.

After repointing, the phone still had pending remote changes and its existing
folder type was Send Only. The owner reported resolving this by switching to
Receive Only and then to Send & Receive. The lasting lesson is to inspect each
device's folder type alongside its path; do not use Override Changes merely to
make an out-of-sync indicator disappear. Choose the final direction according
to whether edits should flow from that device, to it, or both ways.

## Closeout and limits — 2026-09-10

The owner accepted the issue as resolved after the phone split and sync-setting
change. Desktop improvement was measured; phone startup improvement was not.
No phone performance number or isolated causal claim is inferred from that
acceptance. Personal vault contents were not published as part of this record.
