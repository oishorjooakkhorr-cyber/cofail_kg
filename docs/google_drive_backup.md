# Research outputs follow Git push and pull

Automatic Google Drive transfers happen only after a successful Git push or
pull through the PowerShell wrapper. There is no hourly task, logon trigger,
background watcher or automatic retry timer. Commits, edits, fetches, failed
Git commands and dry-run pushes cause no transfers.

Shared backup: [CoFail-KG-Backups](https://drive.google.com/drive/folders/1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk).
Both scripts default to
`cofail_gdrive,root_folder_id=1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk:`.
This rclone connection string pins the existing folder by ID for each command,
without changing your remote configuration. No folder search or My Drive
shortcut is needed. The ID/link grants no access: every developer still needs
their own authentication and the owner's sharing permission. Explicit
`-Destination` overrides remain available for isolated tests or another backup.
After updating an existing installation, reopen PowerShell or dot-source the
activation script again so its destination environment variable is refreshed.

## One-time setup on each computer

1. Download rclone from https://rclone.org/downloads/ and extract it to a
   permanent path, for example `E:\Tools\rclone\rclone.exe`.
2. Create a Google Cloud project, enable the Google Drive API and configure a
   Desktop-app OAuth client using [rclone's current setup guide](https://rclone.org/drive/#making-your-own-client-id).
   Rclone's shared OAuth client is being retired during 2026; do not leave the
   client ID/secret blank for this installation. Then run
   `E:\Tools\rclone\rclone.exe config`, create **cofail_gdrive**, choose **drive**,
   enter your OAuth app's client ID/secret locally and authenticate in the browser.
   For collaboration, each developer signs in with their own Google account and
   receives Editor access to the shared backup folder. Use the `drive` scope
   when access to shared/pre-existing files is required; `drive.file` is limited
   to app-created files. Configure the shared folder explicitly and verify
   visibility before using another computer. OAuth credentials stay in rclone's
   user config outside Git; never upload that config or paste tokens into chat.
   The installed executable on this computer is `E:\Tools\rclone\rclone.exe`.
3. Enable the wrapper in your PowerShell session from the repository root:

   ```powershell
   . .\scripts\enable_cofail_kg_backup.ps1 -RclonePath E:\Tools\rclone\rclone.exe
   ```

   The leading dot and following space are required. Activation itself transfers
   nothing. Then use your ordinary commands:

   ```powershell
   git add .
   git commit -m "Research update"   # no Drive transfer
   git push                        # Git first, then upload eligible outputs
   git pull                        # Git first, then download outputs
   ```

4. For activation in future PowerShell sessions, add this single line to your
   PowerShell profile (`$PROFILE`), adjusting the repository/rclone paths:

   ```powershell
   . 'E:\Phitron Thesis\cofail_kg\scripts\enable_cofail_kg_backup.ps1' -RclonePath 'E:\Tools\rclone\rclone.exe'
   ```

   If your execution policy blocks these local scripts, use a process-scoped
   policy in the session: `Set-ExecutionPolicy -Scope Process Bypass`.
   No profile, credential store or Git hook is edited by the setup script.

Git has no client-side post-push or post-pull hook that covers these commands.
A pre-push hook would upload before knowing whether Git succeeded; merge hooks
would also miss up-to-date pulls and some rebase paths. The wrapper therefore
runs Git first and starts a transfer only after its exit status is zero.
It preserves Git arguments, including `git -C <repository> push/pull`, and
limits transfers to the repository containing the wrapper.

**Scope:** ordinary `git` commands in an activated PowerShell are covered.
GitHub Desktop, VS Code source-control buttons, Git Bash, direct `git.exe`
commands, other shells and Git aliases such as `git publish` bypass this wrapper.
Use the activated PowerShell for pushes/pulls that should transfer outputs.
Only one repository wrapper can be active in a PowerShell session; activate the
corresponding clone when switching computers/checkouts.

If you previously installed the old hourly task, disable it once:

```powershell
Disable-ScheduledTask -TaskName CoFail-KG-Backup
```

No production task was enabled during implementation. The old task-registration
script has been removed. No task is required for the new workflow.

## Other developers using the same backup folder

This setup is per computer and per Google account. Cloning the repository gets
the scripts and this guide; it does not install rclone, authenticate Google, or
enable the PowerShell wrapper automatically. The current implementation supports
Windows PowerShell/PowerShell 7; other operating systems need their own integration.

### Backup owner: grant folder access

In Google Drive, open [the existing CoFail-KG-Backups folder](https://drive.google.com/drive/folders/1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk) and share it with each
developer's Google email as **Editor**. Send them that folder's link so they can
identify the correct folder. Keep general access restricted to invited people.
Do not send your Google password, `rclone.conf`, OAuth token, or OAuth client JSON.
Editors can modify/move/remove shared content through Drive itself; the backup
scripts' preservation rules do not restrict what an editor can do manually.
No collaborator access has been granted by these scripts.

### Developer: install and authenticate independently

1. Clone the repository, then install rclone at a permanent path. Example:

   ```powershell
   git.exe clone https://github.com/oishorjooakkhorr-cyber/cofail_kg.git C:\Work\cofail_kg
   Set-Location C:\Work\cofail_kg
   $rcloneExe = 'C:\Tools\rclone\rclone.exe'
   ```

2. Follow the OAuth setup in the one-time setup section above using **your own**
   Google Cloud project/Desktop OAuth client and Google account. Enable Drive API,
   keep Testing mode, and add your own Google email as a test user. Create the
   rclone remote named `cofail_gdrive` with scope `drive`; keep its advanced
   `root_folder_id` blank and `shared_with_me` false. The scripts supply the
   verified folder ID per command, regardless of its name/location in My Drive.

   ```powershell
   & $rcloneExe config
   ```

   Each developer's token remains on their own computer. Their own OAuth app
   means the backup owner does not need to distribute any authentication settings.
   With Testing mode, each developer reauthenticates about weekly.

3. Open [the shared folder](https://drive.google.com/drive/folders/1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk)
   while signed in to the same account used for rclone. Confirm the owner granted
   your account Editor access. Do not create another folder or copy the contents;
   the scripts address this folder directly by ID. Existing shortcuts may stay,
   but are not used by the default destination.

4. Before any push, verify that you can see the owner's existing backup:

   ```powershell
   & $rcloneExe lsf 'cofail_gdrive,root_folder_id=1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk:current' --dirs-only
   & $rcloneExe lsf 'cofail_gdrive,root_folder_id=1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk:current/results/runs' --max-depth 1
   ```

   The first command should show `data/` and `results/`; the second should show
   existing experiment run directories. If the path is missing/empty, or rclone
   reports duplicate names or a permission error, fix sharing, account selection
   first. Do not change the destination to a same-named personal folder.

5. Activate the wrapper and make the first pull to restore the shared outputs:

   ```powershell
   . .\scripts\enable_cofail_kg_backup.ps1 -RclonePath $rcloneExe
   git pull --ff-only
   ```

   An already-up-to-date Git pull still downloads the backup. Changed local
   outputs are preserved under `.cofail-backup-history/` before replacement;
   Git-tracked files stay managed by Git. Raw datasets, model weights and large
   cache tables are not backed up: follow the README to obtain/rebuild those.

6. For future sessions, put the activation line in the PowerShell profile you
   use, with **your own clone and rclone paths**, then reopen PowerShell:

   ```powershell
   . 'C:\Work\cofail_kg\scripts\enable_cofail_kg_backup.ps1' -RclonePath 'C:\Tools\rclone\rclone.exe'
   ```

   The all-hosts user profile path is `$PROFILE.CurrentUserAllHosts`. If script
   execution is blocked, review `Get-ExecutionPolicy -List`; choosing
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` permits local scripts
   for your user. Organizational policy can still override this. Activation
   must display the Drive-transfers-enabled message before relying on the wrapper.

### Everyday team workflow

```powershell
git pull --ff-only          # pull code, then outputs
# Work and finish writing the outputs; uploads defer files newer than 10 minutes.
git add .
git commit -m 'Research update'  # no Drive transfer
git push                   # push code, then eligible outputs
```

Use unique experiment/run IDs across developers. Avoid concurrent pushes that
change the same output path: this is a shared versioned backup, not a conflict
resolver. The last upload becomes `current`; previous remote versions go into
`history`. Pull before starting work on another computer. GUI Git clients and
direct `git.exe` commands bypass the PowerShell wrapper.

When authorization expires:

```powershell
& $rcloneExe config reconnect cofail_gdrive:
```

Complete browser consent, then retry the failed Git push/pull. A successful Git
operation can have a failed Drive transfer; read the wrapper warning and exit
status rather than assuming both services succeeded.

References: [Google folder sharing](https://support.google.com/drive/answer/7166529),
[rclone folder IDs](https://rclone.org/drive/#root-folder-id),
[connection strings](https://rclone.org/docs/#connection-strings).
This onboarding path is documented from those sources; another developer's
account/computer has not been tested or configured here.

## What is transferred

| Path | Included artifacts |
| --- | --- |
| `results/` | Agent responses, run/trace JSON, diagnostics, logs, reports, reference sets, semantics and historical checkpoints |
| `data/processed/` | Derived tables, populations, manifests and summaries |
| `data/agent_inputs/` | Generated input sheets |
| `data/cache/primekg_metadata.json`, `data/cache/primekg_release.json` | Small provenance metadata |

Allowed formats: CSV, TSV, JSON, JSONL, TXT, LOG, MD, YAML, YML, Parquet, Arrow,
Feather, NPY, NPZ, HTML, PDF, PNG, JPG and SVG. Other extensions, raw datasets,
large cache tables and model files are excluded. Symlinks/junctions and names
identifying environment files, secrets, credentials, tokens, API/private keys,
models and datasets are skipped. Filename rules cannot detect secrets inside
otherwise legitimate outputs; keep credentials out of experiment logs.
Custom output paths outside these roots are not covered.

## Upload after push

Files must be at least ten minutes old and have no open writer. A brief read
lock prevents changes while each file is copied to a temporary snapshot; the
lock is released before network upload. Recent/busy files are logged and will
be reconsidered on the **next push**, never by a timer. A file that is closed
but logically unfinished for ten minutes cannot be distinguished automatically.
Snapshots are per file, not atomic snapshots of a complete experiment.

Rclone uses checksum comparisons to upload only new or changed content:

```text
CoFail-KG-Backups/
  current/<original relative path and filename>
  history/<UTC timestamp plus unique ID>/<previous relative path and filename>
```

Previous remote versions are preserved before replacement. Deleting a local
file does not delete its Drive copy. Every real upload performs a one-way
checksum check of the snapshot. Local snapshots temporarily require disk space
equal to all eligible outputs; local reads are not incremental.

## Download after pull

Git finishes first; a failed pull or unresolved Git conflict prevents the Drive
transfer. Even an already-up-to-date successful pull downloads Drive updates.
Downloads are staged and checksum-verified before local files are changed.
Missing output files are restored. Changed output files are replaced atomically,
and their previous local versions are saved at:

```text
.cofail-backup-history/<UTC timestamp plus unique ID>/<original relative path>
```

That directory is Git-ignored and excluded from Drive backups. Git-tracked files
are skipped by the Drive restore so their versions remain managed by Git.
An existing local writer prevents replacement; the transfer reports failure and
can be retried on the next pull. Local files absent from Drive remain intact.
No local or remote research versions are automatically deleted or expired.

Drive `current` is the latest shared backup, not a commit-specific snapshot or
branch-specific dataset. Pushing from several computers uses last successful
upload wins, with overwritten remote versions retained. Pull before resuming
work on another computer. Pulling deliberately replaces unpushed local output
changes, while retaining those previous bytes in local history as requested.

## Failures, logs, dry runs and verification

GitHub and Drive are separate services: a Git operation can succeed while its
Drive transfer fails. The wrapper warns and sets `$LASTEXITCODE` to 1 for that
case. It never rolls back Git or starts a timed retry. Retry the corresponding
push/pull when connectivity/authentication/storage is fixed. A rejected push or
failed pull performs no Drive transfer. Logs and temporary snapshots are under
`%LOCALAPPDATA%\CoFail-KG-Backup`; histories/logs have no retention limit.

Explicit diagnostics (no uploads or local output replacement):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_cofail_kg.ps1 -RclonePath E:\Tools\rclone\rclone.exe -DryRun
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_cofail_kg.ps1 -RclonePath E:\Tools\rclone\rclone.exe -Pull -DryRun
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_cofail_kg.ps1 -RclonePath E:\Tools\rclone\rclone.exe -VerifyOnly
```

The underlying script remains usable for explicit manual repair after a failed
transfer. To disable this session's wrapper, run `Remove-Item Function:git`;
future sessions remain enabled if the activation line is in your profile.
A forcibly killed transfer can leave a `stage-*` folder under the log directory;
remove only stale staging folders while no transfer is running.

## Local checks

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\test_backup_cofail_kg.ps1 -RclonePath E:\Tools\rclone\rclone.exe
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\test_git_cofail_backup.ps1 -RclonePath E:\Tools\rclone\rclone.exe
```

Tests use real rclone local backends and temporary Git repositories, never
GitHub or Google Drive. They verify incremental upload, retained remote/local
versions, corruption detection, no deletion, busy writers, tracked-file safety,
no transfer on commits/status/failed commands/dry runs, and transfers after
successful push/pull (including already-up-to-date pulls and `git -C`).
Validated on 2026-10-16 with Windows PowerShell 5.1 and rclone v1.75.2.
Google authentication and Drive access were verified on 2026-10-16. The first push-triggered backup uploaded 116 files and its MD5 check reported 116 matches and zero differences. A real cloud restore has not been performed.
Scientific protocols and existing experiment outputs were not modified.

References: [Git hooks](https://git-scm.com/docs/githooks),
[rclone copy](https://rclone.org/commands/rclone_copy/),
[version directories](https://rclone.org/docs/#backup-dir-string),
[checksum checks](https://rclone.org/commands/rclone_check/),
[Drive authentication](https://rclone.org/drive/).

## Setup status on this computer (2026-10-16)

- Installed rclone: `E:\Tools\rclone\rclone.exe`.
- OAuth client settings: `E:\Tools\rclone\oauth-client.json`, outside Git.
- OAuth authorization: saved in the default user rclone config; Drive access verified read-only.
- Wrapper activation added to both Windows PowerShell and PowerShell 7 current-user
  all-hosts profiles; verified in new processes using `git --version` only.
- Windows PowerShell CurrentUser execution policy set to RemoteSigned with user approval.
- No hourly scheduled task exists. The S12-S14 GitHub push and its first Drive backup completed successfully.
- `CoFail-KG-Backups/current` was created by the successful wrapped push. All
  116 stable files passed checksum verification. Two open Ollama server logs
  were deferred; their committed versions are retained on GitHub.

The researcher chose **weekly reauthentication** on 2026-10-16. Keep the OAuth
app in Testing mode; publishing, a homepage and a privacy-policy site are not
required for this chosen workflow. Google limits this Testing-mode Drive refresh
token to **seven days**. When a transfer reports expired/revoked authorization,
reauthenticate locally, then retry the corresponding Git push/pull:

```powershell
E:\Tools\rclone\rclone.exe config reconnect cofail_gdrive:
```

Only approved test users may authorize this app. Other developers must use their
own Google accounts, receive access to the shared backup folder, and configure
that folder explicitly; never share this machine's rclone config/token. See
[Google's refresh-token expiration rules](https://developers.google.com/identity/protocols/oauth2#expiration).
