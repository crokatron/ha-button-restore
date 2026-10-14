# HA Button Restore: maintainer handover

[One-screen summary](START-HERE.md) · [User manual](USER-MANUAL.md) · [Feature overview](../README.md) · [Recorded validation](../VALIDATION.md)

## Purpose and behaviour to preserve

Give a temporary button action an intelligent restore. Capture selected HA entity states before a sequence such as lights off and dehumidifiers off; later restore only devices that have not received a newer HA control command. The logic runs inside Home Assistant, without a browser or Projects server staying open.

- **Capture:** Remember selected entity states under a named key before changing them. (HA action.)
- **Restore:** Restore eligible captured entities once using the same key. (HA action.)
- **Later-command priority:** A newer HA service command invalidates restoration for that device, even if its displayed state did not change. (Automatic.)
- **Physical-device grouping:** Related control entities on the same registered device invalidate together. (Automatic.)
- **Clear:** Discard a remembered group without restoring it. (HA action.)
- **Button-independent:** Works with any button integration that exposes usable triggers; this component does not discover press types. (Integration boundary.)

The [demo](../demo.html) is a smaller, labelled simulation with fictional data. It explains cause and effect without the real service; it is not evidence of a working production installation. Numbered screenshots in the user manual distinguish actual-app captures from demo captures.

## Files and sources of truth

| Actual package path | Maintainer role |
| --- | --- |
| [projects-host/ha-custom-components/mungoon_button_restore](../projects-host/ha-custom-components/mungoon_button_restore) | HA integration and policy |
| [projects-host/test_button_restore_priority.py](../projects-host/test_button_restore_priority.py) | Command-priority fixtures |
| [examples/button-restore-scripts.yaml](../examples/button-restore-scripts.yaml) | Example scripts; entity IDs must be adapted |
| [demo-source](../demo-source) | Editable demo HTML/CSS/runtime and embedded screenshot tour |
| [SOURCE-MANIFEST.json](../SOURCE-MANIFEST.json) | Original copied-source paths and SHA-256 checkpoint values |

The original working source is under C:/Users/lamon/Desktop/AI TOOLS/NAS for NAS modules; adjacent CAD/watch source locations are recorded by the full backup’s reviewed source manifest. This package contains only the explicitly copied source, not an automatic mirror. The main private nas-projects backup retains the broader shared host context.

## Setup, run and tests

Run commands from this repository root unless a `cd` is shown. Use a disposable checkout and fictional data for first setup. Dependencies, SDKs, signing material and personal data are not bundled. The following are continuation instructions grounded in the retained source, **not commands executed or newly certified by this handover**.

```powershell
python -B projects-host/test_button_restore_priority.py
```

Install the integration directory into HA /config/custom_components, restart after configuration validation, then add Layout Studio button restore. Follow docs/button-restore.md.

Selected project check:

```powershell
python -B projects-host/test_button_restore_priority.py
```

For the documentation demo alone, serve this repository on loopback with `python -m http.server 8765 --bind 127.0.0.1` and open `/demo.html`. Choose a free port if another preview is running. JavaScript syntax can be checked with `node --check demo-source/runtime.js`. `python demo-source/rebuild.py` rewrites demo.html, so run it only in a disposable checkout or an authorised demo-editing session. A local server cannot provide missing HA/CAD/NAS functions. Inspect browser tests for installed dependencies, fixture requirements and network targets before running them with the approved browser tooling.

## Data, configuration and backup boundaries

Capture/restore use the same key and explicit entities. Snapshots are memory-only and consumed once; restarts are not recoverable undo history. The integration uses HA runtime facilities, not a browser service.

Snapshots exist in HA memory. They are not a database or a cross-restart backup. A failed capture clears an old snapshot and stops the sequence; all requested entities must be available at capture time.

Git preserves reviewed source and documentation. It does not copy browser storage, application databases, uploaded models/photos, accepted device settings, SDKs or credentials. Maintain independent recovery copies of the data identified above, including matching configuration and asset versions. Never add real secrets to examples, issues or logs. Private source copies on GitHub are not proof of a complete NAS/offsite data backup.

## Current verification and Git state

Before these documentation edits on 14 October 2026, this package was clean on branch `main` at `5a92172a604d702458de436d27ffd8f0fc76889d` and its private upload was verified. All 8 manifest-listed source entries matched their stored checksums before editing. The upload follow-up has completed all 17 repositories and is paused; it does not run this tool or back up its live data.

These handover pages and README links accompany the private source package. Preserve them when continuing; stage only reviewed changes. Recheck current `git status --short --branch` and `git diff` before starting. No project-specific background schedule was inspected or changed in this documentation pass. Any service schedules in older notes are historical claims to verify in the actual deployment.

Earlier package checks and limits are recorded in [VALIDATION.md](../VALIDATION.md). This handover adds documentation/link/whitespace/secret and source-preservation checks only. No current NAS release, real hardware state, fresh installation, complete data restoration or offsite-backup freshness was verified here.

## Recovery approach

1. Preserve the current installation/data before changing it. Identify the exact code commit and data snapshot required; do not assume this package matches the running service.
2. Recover source into a new folder. Verify the source manifest and restore the project-specific configuration/assets described above separately. Recreate dependencies from the retained project files and guides.
3. Restore user data into an isolated instance or clean test browser. Check a representative editable record, associated files and save/reload behaviour, then compare to the original. Do not test recovery by overwriting production.
4. Record what actually restored and what remains missing. A demo opening or a passing syntax check is not a production recovery drill. Real deployment/device actions need the existing authorised workflow.

## Known limits and next work

Direct changes through a physical remote or vendor application may not produce a HA service event and are not universally tracked. This is targeted restore, not general undo. Eight policy tests passed previously; a clean HA installation has not been rerun for this documentation update.

**Priority:** Test capture→off→restore and capture→off→newer off→restore on a spare entity, including another entity of the same physical device. Check compatibility with the target HA version; vendor-app/remote changes may not emit tracked HA commands.

Common symptoms to check for this tool:

- Restore does nothing: check key spelling, whether the snapshot was already consumed, and whether HA restarted.
- One device stays unchanged: inspect commands issued after capture; it may be intentionally ineligible.
- Single press never runs: check the button’s actual HA events and automation trigger.
- Unavailable entity: fix availability before capture rather than carrying forward an older snapshot.

Keep [the release checklist](../RELEASE-CHECKLIST.md) and [third-party notes](../THIRD-PARTY.md) with the package. Original contributions use MIT; bundled/upstream code and assets keep their own licences. Public publication is a separate decision; preparing documentation is not permission to publish.
