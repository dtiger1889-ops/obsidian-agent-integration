# Syncthing setup: desktop ↔ phone, from nothing

This is the full build of the sync layer under the rest of this repo: a
Windows desktop and an Android phone, each holding a live copy of the Obsidian
vault, kept in step by Syncthing with no cloud in the middle. Follow it top to
bottom and you end with the same setup this system runs every day, including
the optional second share that puts the agent's workspace notes on the phone.

Everything below comes from the running configuration, read off the desktop's
Syncthing API, plus the incidents that shaped it. Where a step exists because
something broke, the break is named. Every value that belongs to your machines
(device IDs, paths, addresses) is written as a `<placeholder>`.

---

## What you end up with

```
 Windows desktop                                   Android phone
 ───────────────                                   ─────────────
 Syncthing (per-user, starts at logon)             Syncthing-Fork (foreground service)
 GUI on 127.0.0.1:8384 only                        GUI in the app drawer
        │                                                 │
        │  share "obsidian-vault"   send & receive        │
 <vault folder> ◄──────────────────────────────────────► /storage/emulated/0/<VaultFolder>
        │                                                 │   opened in Obsidian as a vault
        │  share "agent-workspace" (optional, md only)   │
 <workspace folder> ◄──────────────────────────────────► /storage/emulated/0/<WorkspaceVault>/<WorkspaceFolder>
                                                          │   parent opened as a SECOND vault
        └──────── LAN, or Tailscale when away ────────────┘
```

| Piece | Desktop | Phone |
|---|---|---|
| App | Syncthing, installed with the *Syncthing Windows Setup* package (Bill Stewart's per-user installer) | **Syncthing-Fork**, package `com.github.catfriend1.syncthingfork`, installed from **F-Droid** |
| Runs as | Ordinary user process, launched by a Task Scheduler logon task (`stctl.exe --start`) | Android foreground service |
| GUI | `http://127.0.0.1:8384`, loopback only | Drawer → Web GUI |
| Config | `%LOCALAPPDATA%\Syncthing\config.xml` (also holds the REST API key) | App-private; not readable without root |
| Shares | `obsidian-vault` (whole vault), `agent-workspace` (optional, markdown only) | The same two IDs, accepted from the desktop |
| Versions at time of writing | Syncthing v2.1.5; installer 2.1.1 | Current F-Droid build |

Two independent pieces sit next to this and are **not** part of the sync:

- **Backup.** Two-way sync copies a deletion or a corruption to every device
  within seconds. The vault has its own nightly one-way backup with 7 days of
  retention, separate from Syncthing. Build that before you trust any of this
  with notes you care about. File versioning inside Syncthing is left off here
  *because* the real backup exists; if you have no backup yet, turn on
  Syncthing's *Staggered* versioning as a stopgap.
- **Tailscale** (optional). Lets the phone reach the desktop over cellular. The
  sync works on home Wi-Fi without it.

---

## Part 1: Desktop install (Windows)

1. Install the per-user Windows package:

   ```powershell
   winget install BillStewart.SyncthingWindowsSetup
   ```

   Choose the **current-user** install, not the service install. The
   installer creates three things that matter later:
   - `%LOCALAPPDATA%\Programs\Syncthing\syncthing.exe` and `stctl.exe`
   - a Task Scheduler task named `Start Syncthing at logon (<user>@<PC>)`
     whose action is `stctl.exe --start`, triggered at logon
   - inbound Windows Firewall permission for Syncthing. On this machine that
     ended up as two program rules for `syncthing.exe` (one TCP, one UDP, any
     port). Sync uses TCP/QUIC 22000 and local discovery uses UDP 21027, so
     the rules must allow both protocols.

2. Open `http://127.0.0.1:8384`. Leave the GUI bound to `127.0.0.1`. That is
   what stops other machines on the network from reaching it, so a GUI password
   is optional here; set one anyway if other people use the PC. If you ever
   bind the GUI to `0.0.0.0`, a password and HTTPS become mandatory.

3. Set your home Wi-Fi network profile to **Private** in Windows, and check
   that the Syncthing firewall rules cover the profile you are actually on
   (*Windows Defender Firewall → Inbound Rules → syncthing.exe → Advanced*).
   A rule limited to Private does nothing while Windows thinks you are on a
   Public network, and the phone simply fails to connect.

4. Name the device something you will recognise on the phone:
   *Actions → Settings → General → Device Name*.

5. Leave the global defaults that matter here as they are, and confirm them:

   | Setting | Value | Why |
   |---|---|---|
   | Sync Protocol Listen Addresses | `default` | TCP and QUIC on 22000 |
   | Global discovery / local discovery / relaying / NAT traversal | all on | Lets the phone find the PC on any network |
   | Anonymous usage reporting | declined | Your call |

---

## Part 2: Phone install (Android)

1. Install **F-Droid**, then install **Syncthing-Fork** from it.

   **Why F-Droid and not the GitHub release:** the fork's GitHub repository
   was transferred off its original author's account to a different account.
   A transfer like that can be an honest handover or a takeover used to ship a
   tampered APK, and from the outside you cannot tell which. F-Droid builds the
   app from source and signs it with its own key, which is an independent
   check. So install from F-Droid, **and keep updating from F-Droid**. Do not
   switch to APKs from the GitHub repo unless you can confirm the transfer was
   legitimate. (The original upstream Android app was discontinued; the fork is
   the maintained one.)

2. Grant the permissions it asks for on first run:
   - **All files access.** It must write to shared storage, where Obsidian
     can open the folder.
   - **Notifications.** Android requires this for the foreground service.
   - **Ignore battery optimisation.** Without this exemption Android freezes
     the service and sync stops whenever the screen is off.

3. In Syncthing-Fork's settings, set **Run conditions**:
   - Run on Wi-Fi: on.
   - **Run on mobile data: on**, if you want sync away from home. Skip it and
     the phone only syncs on Wi-Fi.
   - Charging-only / power-saving conditions: off, unless you prefer slower
     sync over battery.

4. Install **Obsidian** from the Play Store. Do **not** create a vault yet.

---

## Part 3: Pair the two devices

1. On the desktop: *Actions → Show ID*. A QR code and a device ID
   (`XXXXXXX-XXXXXXX-…`) appear.
2. On the phone: *Devices → +*, then scan the QR code. Give the desktop a
   name. Leave **Addresses** as `dynamic`.
3. On the desktop, accept the "new device wants to connect" banner. Leave
   *Introducer* and *Auto Accept* **off** on both sides. Auto-accept is what
   creates folders with the wrong ID (see Part 4, step 4).
4. Both GUIs should show the other device as **Connected**.

---

## Part 4: The vault share

The desktop creates the share and the phone **accepts** it. Doing it the other
way around is the most common way to end up with two folders that never link.

1. **Before sharing anything, write the vault's ignore file.** Create
   `<vault folder>\.stignore`:

   ```
   // vault share must never sync the workspace subtree; it is its own share
   /<WorkspaceFolder>
   ```

   You only need this line if you will build the optional workspace share in
   Part 6. Without Part 6, an empty `.stignore` (or none) is fine. Obsidian's
   own `.obsidian/` config folder **is** synced deliberately, so plugins and
   settings follow you to the phone.

2. Desktop: *Add Folder*.

   | Field | Value |
   |---|---|
   | Folder Label | anything readable |
   | **Folder ID** | a fixed, readable ID such as `obsidian-vault`. This ID is what links the two ends, not the label and not the path |
   | Folder Path | `<vault folder>` |
   | Sharing tab | tick the phone |
   | Advanced → Folder Type | **Send & Receive** |
   | Advanced → Watch for Changes | on (the file-system watcher) |
   | Advanced → Full Rescan Interval | 3600 s |
   | File Versioning | None if you have a real backup; *Staggered* if not |

3. Leave these advanced folder settings at the values below. The GUI defaults
   match, but check `junctionsAsDirs` in the config, because its default has
   flipped between Syncthing versions:

   | Setting | Value | Why |
   |---|---|---|
   | `junctionsAsDirs` | **false** | Syncthing does not follow Windows junctions. If you ever put a junction inside the vault, the phone never sees what is behind it and nothing leaks through |
   | `fsWatcherDelayS` | 10 | Batches rapid saves into one sync |
   | `maxConflicts` | 10 | Caps conflict copies per file |
   | `ignorePerms` | false | Default |
   | `autoNormalize` | true | Unicode filename normalisation between OSes |

4. **Phone: accept the offer, do not create a folder.** A card appears saying
   the desktop wants to share `obsidian-vault`. Accept it. It arrives already
   carrying the desktop's folder ID.

   If you instead tap *+ Folder* and make a new one, the phone generates a
   random ID (it looks like `abcde-fghij`). That folder never links to the
   desktop's, and both sides sit "Up to Date" while syncing nothing.

   **If the offer card never appears** (it happened once here): create the
   folder on the phone manually and type the desktop's folder ID **exactly**,
   then tick the desktop under sharing. Matching ID = same folder.

5. Phone folder path: pick a **top-level folder in shared internal storage**,
   `/storage/emulated/0/<VaultFolder>`. Do not use app-private storage, and
   do not use the Android/data tree, because Obsidian needs to open it.
   Folder type: **Send & Receive**.

6. Wait for the first sync to reach **Up to Date** on both sides.

7. Phone Obsidian: *Open folder as vault* → pick
   `/storage/emulated/0/<VaultFolder>`. The vault opens with the desktop's
   notes, plugins and settings.

**Folder type is a real choice.** Send & Receive means edits flow both ways.
Send Only on a device means its changes go out but others' do not come in;
Receive Only is the reverse. A device stuck on the wrong type shows pending
items that never clear. Check each device's type alongside its path, and
**never press "Override Changes"** just to clear an out-of-sync badge, because
it overwrites the other side.

---

## Part 5: Obsidian settings that keep sync quiet

These are Obsidian settings, not Syncthing ones, but each prevents a class of
sync mess seen in practice.

- **Attachments go in one fixed folder.** *Settings → Files and links →
  Default location for new attachments → In the folder specified below*, set to
  an `Assets/` folder. Pasted images then never land beside notes, or in any
  linked folder.
- **Write-on-open plugins must ignore anything that is not your notes.**
  Templater (`ignore_folders_on_creation`) and Linter (`foldersToIgnore`) will
  rewrite files they consider new or changed. Any folder surfaced in a vault
  (a workspace link, a template folder) goes on both ignore lists before it
  appears.
- **Don't keep Obsidian open on both devices while one is still syncing.**
  Obsidian rewrites `.obsidian/app.json`, `community-plugins.json` and its
  workspace state on launch and close. If the phone opens the app while the
  desktop still has unsynced config, you get conflict copies of files nobody
  edited, and the stale copy can win. That happened once here: a
  7-plugin list beat the correct 9-plugin list, so newly installed plugins
  would not enable on either device. Let the desktop's Syncthing show
  **Up to Date** before opening Obsidian on the phone.
- Some settings are per-device and not in the synced config at all. After
  first sync, spot-check that each plugin you rely on is actually enabled on
  the phone.

---

## Part 6 (optional): Put the agent workspace on the phone

This is the second share. It makes the agent's project notes (CHECKPOINTs,
specs, READMEs) readable and editable from the phone without syncing the
workspace's databases, builds or git internals.

### Why it is a separate share and a separate vault

The first version of this put a Windows **junction** to the workspace
*inside* the personal vault. On the desktop that worked: links from vault
notes resolved to the live project files. It had two costs:

1. **The phone never saw it.** Syncthing does not follow junctions
   (`junctionsAsDirs=false`), so the phone needed its own share regardless.
2. **Startup got slow.** The vault registered about 139,000 filesystem
   entries, nearly all of them through the junction, although only about
   5,600 were Markdown notes. Desktop Obsidian took about nine seconds to
   start. Moving the junction into a separate, on-demand vault brought it to
   about 1.3 seconds. (Full record:
   [workspace-startup.md](workspace-startup.md).)

So the layout is: the personal vault stays small, and the workspace gets its
own vault on each device.

### Desktop

1. Make a wrapper folder for the second vault, then a junction inside it
   pointing at the real workspace:

   ```powershell
   New-Item -ItemType Directory "<workspace vault folder>"
   New-Item -ItemType Junction -Path "<workspace vault folder>\<WorkspaceFolder>" -Target "<workspace folder>"
   ```

   Open `<workspace vault folder>` in Obsidian as a vault. Give that vault
   **no community plugins**, and turn **off** *Automatically update internal
   links*, so opening it can never rewrite a project file.

   **Removing a junction:** `fsutil reparsepoint delete "<junction path>"`,
   then remove the now-empty folder. Never `rm -rf`, `Remove-Item -Recurse`,
   or an Explorer delete on a junction: they follow it and delete the real
   workspace behind it.

2. Write `<workspace folder>\.stignore` **before** adding the share, so the
   first scan can never pick up a database:

   ```
   // md-only share: workspace markdown to the phone, nothing else
   .git
   node_modules
   __pycache__
   .venv
   venv
   !*.md
   *
   ```

   Order matters. Syncthing uses the **first** pattern that matches. The
   directory prunes come first. Then `!*.md` keeps Markdown. The final `*`
   drops everything else. An include-only list without the closing `*` fails
   open: anything the list forgot gets synced, including a live database.

3. *Add Folder*: ID `agent-workspace` (any fixed ID), path
   `<workspace folder>`, **Send & Receive**, share with the phone, **no
   versioning is fine only if the workspace is backed up elsewhere**.

4. **Verify before the phone joins.** With the phone not yet ticked (or the
   share paused), let the desktop scan and check that the file count and size
   look like Markdown only (here: about 1,600 files and 17 MB, against a
   workspace of about 20 GB). If the size is in gigabytes, the ignore file
   is wrong. Fix it before any other device sees the share.

### Phone

1. Accept the `agent-workspace` offer (same rule as Part 4: accept, don't
   create).
2. Path: `/storage/emulated/0/<WorkspaceVault>/<WorkspaceFolder>`. The share
   writes one level **below** a wrapper folder, the same shape as the
   desktop.
3. Obsidian: *Open folder as vault* → `/storage/emulated/0/<WorkspaceVault>`,
   the **parent**. Switch back to the personal vault when finished. Obsidian
   reopens whichever vault was last used, and the big one is slow to load.
4. Also put `/<WorkspaceFolder>` in the phone's **personal-vault**
   `.stignore` if the workspace folder ever sat inside the personal vault on
   the phone. Keep that line for as long as that subtree exists anywhere.

### Moving a share's path later

The ordinary *Edit Folder* dialog shows the path as locked. To move a share:

1. Pause the share.
2. Move the files yourself. Syncthing does not move them.
3. *Actions → Advanced → Folders → <the folder> → Path*, change **only** the
   path, save, read it back.
4. Resume. The folder ID, sharing, ignores and type are all preserved.
5. In Obsidian, *Open folder as vault* on the new location. Changing
   Syncthing's path does not register a vault.

---

## Part 7 (optional): Sync away from home with Tailscale

1. Install Tailscale on both devices and sign in to the same tailnet.
2. On the phone, Syncthing-Fork → Run conditions → **Run on mobile data: on.**
   Tailscale being connected is not enough. Android still classifies a
   Tailscale connection over cellular as mobile data, and Syncthing-Fork
   refuses port 22000 until this condition allows it. What you see: Tailscale
   pings the phone fine, but TCP `<phone tailnet IP>:22000` is actively
   refused.
3. Addresses stay `dynamic`. If discovery is slow to find the PC over the
   tailnet, edit the desktop device **on the phone** and add a static address
   alongside `dynamic`:

   ```
   dynamic, quic://<desktop tailnet IP>:22000
   ```

A healthy remote connection shows in the desktop GUI with the phone's
Tailscale address (a `100.x.y.z` or `fd7a:115c:a1e0::…` address).

---

## Part 8: Verify the whole thing

Do this after setup and after any change. "Both apps are open" is not a check.

**GUI:** each share **Up to Date** on both devices, 0 failed items, remote
device shows 100%.

**API (desktop, PowerShell):** these read the real state. Use them when the
GUI looks fine but a file hasn't arrived.

```powershell
[xml]$c = Get-Content "$env:LOCALAPPDATA\Syncthing\config.xml" -Raw
$h = @{ 'X-API-Key' = $c.configuration.gui.apikey }
$api = 'http://127.0.0.1:8384/rest'

Invoke-RestMethod "$api/system/version" -Headers $h                       # version
(Invoke-RestMethod "$api/system/connections" -Headers $h).connections    # phone connected? which address?
Invoke-RestMethod "$api/db/status?folder=obsidian-vault" -Headers $h     # state, globalFiles, needFiles
Invoke-RestMethod "$api/db/completion?folder=obsidian-vault&device=<phone device ID>" -Headers $h   # phone's completion + sequence
Invoke-RestMethod "$api/config/folders/obsidian-vault" -Headers $h | Select-Object type,junctionsAsDirs,fsWatcherEnabled,rescanIntervalS
```

On macOS/Linux the same calls work with
`curl -H "X-API-Key: <key>" http://127.0.0.1:8384/rest/...`, key from the
`<apikey>` element of the config file.

**End-to-end test:** create a note on the phone, see it on the desktop, edit it
there, see the edit on the phone, delete it on one side, confirm it is gone on
the other.

---

## Operating rules (the ones that were learned the hard way)

### Scripted file changes need a forced rescan

Syncthing's file watcher reliably catches edits made through Obsidian or
Explorer. It does **not** reliably catch bulk or scripted changes: `rm`,
`Remove-Item`, `Copy-Item` into `.obsidian/plugins/`, an agent moving twenty
notes at once. What you see: the files are gone (or new) on disk, Syncthing
reports 100% and nothing needed, and the phone never changes. That happened
twice here: a batch delete of conflict files, and a scripted plugin install
that never reached the phone.

After any scripted write, force the scan and confirm it:

```powershell
Invoke-RestMethod -Method Post "$api/db/scan?folder=obsidian-vault" -Headers $h
# or just one subtree:
Invoke-RestMethod -Method Post "$api/db/scan?folder=obsidian-vault&sub=.obsidian/plugins" -Headers $h
```

Then re-read `db/status` (item counts move) and `db/completion` for the phone
(its `sequence` advances). An agent that writes to the vault should do this as
the last step of every batch.

### Conflict copies: diff before you delete

When both devices change a file before they sync, Syncthing keeps the version
with the newer modification time as the live file and saves the other as
`<name>.sync-conflict-<date>-<time>-<deviceID>.<ext>` beside it. The newer
timestamp is not necessarily the version you wanted.

1. Find them all: search for `sync-conflict`, **including `.trash/`**. The phone
   counts conflict files in Obsidian's trash as live conflicts, and its
   badge will not clear until those are gone too.
2. Diff each copy against its live file. Usually the copy is an older snapshot
   with nothing unique. Sometimes it holds an edit that lost the race. One
   here held an instruction to the agent that had never been acted on.
3. Merge anything unique into the live file by hand, then delete the copy. The
   deletion syncs.
4. For `.obsidian/` config conflicts, check which one is actually current
   before choosing (`GET /rest/db/file?folder=obsidian-vault&file=<path>` shows
   each device's version). The stale copy can be the live one.
5. If you removed the copies with a script, force a rescan (above).

### After a reboot, check the process, not the task result

Once after a restart, the logon task reported success (result `0`) but no
Syncthing process was running and nothing listened on 8384 or 22000. At the
same time the phone had stopped accepting connections on mobile data. Neither
failure announced itself. The deeper cause of the first was never found, so
the check is the fix:

1. Desktop: is `syncthing.exe` running, and is something listening on
   22000? If not, run the existing logon task manually
   (`Start-ScheduledTask -TaskName "Start Syncthing at logon*"`). Do not
   reinstall.
2. Wi-Fi profile still **Private**; Syncthing firewall rules still enabled for that profile.
3. Phone: open Syncthing-Fork and confirm the service is running. If you are
   on cellular, check that **Run on mobile data** is on; toggle it off and on
   if the state looks stuck.
4. Tailscale ping succeeds but port 22000 is refused → the phone app isn't
   listening, not a broken tunnel.

### Never put the vault under a cloud-drive folder

Google Drive, OneDrive or Dropbox syncing the same folder as Syncthing means
two engines writing one tree, and a steady supply of conflict copies. Keep the
vault outside any cloud-synced path. Back it up with a one-way job instead.

### Syncthing needs the PC awake

Capture on the phone works offline; the note simply waits. It reaches the
desktop, where the agent files it, the next time both devices are running and
connected. A sleeping PC is the usual reason a capture "didn't sync."

---

## If you use an iPhone, iPad or Mac

This system runs on Windows and Android. **None of the Apple steps below were
run here.** They come from Syncthing's own client list and from people who
run the Apple version, with sources at the end of the section. Treat them as a
checklist of known traps, not as a tested build.

### iPhone and iPad: the three differences that matter

**1. There is no official Syncthing app, and nothing syncs in the background.**
iOS does not let an app run a sync service all the time. The two third-party
clients are:

| Client | Cost | Notes |
|---|---|---|
| **Möbius Sync** | Free up to 20 MB of synced data, then a one-time unlock; a separate paid "Pro" edition also exists | The long-standing option. Syncing into another app's folder, which is what Obsidian needs, is marked *experimental* by its developer |
| **Synctrain** | Free, open source | Newer. Listed on Syncthing's own community-clients page. Needs a recent iOS. Built-in Shortcuts actions |

Either way, iOS pauses the app soon after you leave it. Users report that
background sync stops until the app is opened again. So:

- Sync happens **while the sync app is open**, plus whatever short background
  time iOS allows. Everything in this guide that assumes an always-running
  phone (Part 7, the "PC awake" rule) now applies to **both** ends: the
  iPhone and the PC must both be awake and running Syncthing at the same time.
- The usual workaround is a **Shortcuts automation**: when Obsidian opens,
  first open the sync app, wait 15–60 seconds (longer for a big vault), then
  open Obsidian. Synctrain can trigger a sync from Shortcuts directly. Do the
  same in reverse before you put the phone down after writing something.
- Part 2's Android settings (battery exemption, **Run on mobile data**) have
  no iOS equivalent. Allow the app Background App Refresh and Local Network
  access when iOS asks, and expect nothing more.

**2. Obsidian on iOS can only open vaults inside its own folder.**
On Android you can point Obsidian at any folder in shared storage. On iOS,
Obsidian sees only its own app folder (*Files → On My iPhone → Obsidian*, or
the Obsidian folder in iCloud Drive). A sync client by default writes into
*its own* folder, where Obsidian cannot see it. That is the most common
"it synced but the vault isn't there" report. So the order is reversed from
Part 4:

1. In Obsidian on the iPhone, **create an empty vault** with the same name,
   and turn **off** *Store in iCloud*. It must live under *On My iPhone*.
   iCloud plus Syncthing on one folder is two sync engines on one tree, the
   same problem as a cloud-drive folder on the PC.
2. In the sync app, add the share with the desktop's **exact folder ID**
   (Part 4, step 4 still applies), and use the client's *pick external /
   existing folder* option to choose **that vault folder itself**, inside
   *On My iPhone → Obsidian*. The share's top must be the vault's top, the
   same as on the desktop. After picking, check the path the app shows. If it
   points back into the sync app's own folder, remove the share and pick
   again.
3. iOS shows a warning about syncing outside the app's own storage. That is
   expected with this setup.
4. Let it finish, then open the vault in Obsidian.

**3. Things that break later on iOS.**
- **The `.stfolder` marker can disappear** after an app update. Syncthing then
  stops the folder with a "folder marker missing" error. Fix: re-link the
  external folder in the sync app, and let it rescan before writing anything.
- **First connection means `.obsidian/` conflicts.** The empty iOS vault has
  its own fresh config files, so expect conflict copies of `.json` settings on
  the first sync, and expect to re-enable plugins and themes on the iPhone.
  Resolve them with the conflict rules above: the desktop's copy is almost
  always the one to keep.
- **Test first.** Several people who run this say to set it up with a test
  vault, then point it at the real one. Have a backup before the real one.
- **Keep large or irrelevant folders out.** An iPhone keeps a full local copy
  of every synced file. Add `.git`, attachments you never read on the phone,
  and anything big to the phone-side ignore, or use Synctrain's selective
  sync.
- Part 6 (the workspace share) works the same way, as a **second** vault
  folder under Obsidian's folder with its own external-folder link.

**If you want it hands-off:** the honest alternative on iOS is Obsidian's paid
Sync service. It keeps changes on a server, so the two devices do not have to
be awake together. Syncthing is free and private. On iOS the price is
opening an app before and after you write.

### Mac as the desktop

Everything in Parts 3–8 carries over. The differences:

- **Install:** the open-source `syncthing-macos` app (a menu-bar wrapper,
  listed by Syncthing), or a Homebrew install run as a login service. The
  GUI is the same `127.0.0.1:8384`; the config and API key live under
  `~/Library/Application Support/Syncthing/`.
- **Permissions:** macOS asks before any app reads `~/Documents`, `~/Desktop`
  or external drives. Allow it, or the folder shows errors. Allow incoming
  connections when the firewall asks.
- **Keep the vault out of iCloud.** If *Desktop & Documents Folders* is on
  in iCloud settings, `~/Documents` is iCloud-synced. A vault there is two
  sync engines again, and *Optimize Mac Storage* can remove local copies,
  so Syncthing and search see placeholders instead of notes. Use a folder
  iCloud does not touch, such as `~/Obsidian/<vault>`.
- **Symlinks, not junctions.** Part 6's Windows junction becomes a symlink
  (`ln -s <workspace folder> "<workspace vault folder>/<WorkspaceFolder>"`).
  Syncthing does not follow symlinks inside a share, so the phone still needs
  its own workspace share. Remove a symlink with `rm <link>` and **no**
  trailing slash or `-r`. With either, the command acts on the folder
  behind the link.
- **Filenames:** macOS disks are case-insensitive by default, like
  Windows. Two notes whose names differ only in capitals, created on an
  Android or Linux device, collide. Syncthing reports it as a case conflict
  instead of overwriting. Rename one.
- The PowerShell API snippets in Part 8 become the `curl` form shown there.

Sources for this section:
[Syncthing community clients](https://docs.syncthing.net/users/contrib.html),
[Syncthing forum: Syncthing on iOS/iPadOS](https://forum.syncthing.net/t/syncthing-on-ios-ipados/24610),
[Obsidian forum: Syncthing + Möbius Sync setup](https://forum.obsidian.md/t/sync-mac-pc-and-ios-using-syncthing-mobius-sync/72022),
[Obsidian forum: Synctrain vault not visible on iPad](https://forum.obsidian.md/t/using-synctrain-on-ipad-ipados-18-6-unable-to-access-the-synced-vault/104343),
[Möbius Sync: syncing files from other apps](https://github.com/MobiusSync/MobiusSync/discussions/102),
[Synctrain source](https://github.com/pixelspark/sushitrain),
[Stephan Miller: syncing Obsidian on iPhone for free](https://www.stephanmiller.com/sync-obsidian-iphone-ipad-free/).
Checked 2026-09-24. Prices and app features change, so check the App Store
listing before you rely on either.

---

## Rebuild checklist

For a new phone, a reinstalled PC, or starting over:

1. [ ] Desktop Syncthing installed per-user; logon task present; Wi-Fi Private; firewall allows syncthing.exe TCP+UDP; GUI on `127.0.0.1:8384`.
2. [ ] Phone: F-Droid → Syncthing-Fork; all-files access, notifications, battery exemption; run conditions set.
3. [ ] Devices paired by QR; introducer and auto-accept off.
4. [ ] Vault `.stignore` written **before** sharing.
5. [ ] Desktop share created with a fixed folder ID, Send & Receive, watcher on, `junctionsAsDirs=false`.
6. [ ] Phone **accepted** the offer (or manual add with the identical ID); path in shared storage; Send & Receive.
7. [ ] Phone Obsidian → *Open folder as vault* on that path.
8. [ ] Attachments folder fixed; Templater/Linter ignore lists cover any non-note folder.
9. [ ] Optional workspace share: md-only `.stignore` first, size verified before the phone joins, separate vault on each device.
10. [ ] Optional Tailscale: installed both sides, **Run on mobile data** on, static `quic://` address if discovery lags.
11. [ ] Part 8 verification passes, including the create/edit/delete round trip.
12. [ ] Independent backup of the vault running, because sync is not a backup.
