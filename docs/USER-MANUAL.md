# HA Button Restore — visual user manual

[Project overview](../README.md) · [Offline interactive demo](../demo.html)

Start with the numbered picture guide. Each number identifies the exact highlighted control. Work through one step at a time; the longer reference is below it.

### Try the working offline example

Screenshot of this project’s interactive demo. Side-by-side services are explicitly simulated.

![HA Button Restore — numbered controls](images/guide-1.jpg)

1. **Remember, then turn off.** Single press captures the group before applying the temporary action.
2. **Let another automation run.** A later OFF command takes priority even if the device already looks off.
3. **Restore only eligible devices.** After double press, the lamp returns on while the scheduled-off dehumidifier stays off.

## Detailed task reference

### Understand the sequence

1. Suppose a lamp is on. A single press captures that state, then switches the lamp off for a temporary scene.
2. A double press restores the lamp only if no newer HA command has claimed it. If a scheduled lights-off automation ran in the meantime, the lamp stays off.
3. Use the same key for capture and restore. Separate unrelated buttons/scenes with different keys to avoid replacing each other’s snapshots.

### Assign a group to one button

1. Identify the exact single-press trigger provided by your physical button integration. Choose the devices to affect.
2. In the single-press automation, call mungoon_button_restore.capture first, with key and entity_id list. Follow it with the desired light, fan, switch or other HA actions.
3. In the double-press automation, call mungoon_button_restore.restore with that same key. There is no need to manually guess the previous on/off values.
4. Start with one test light, then expand the group. Confirm your button supports double press; a label in a builder cannot create an event the hardware never emits.

### Test a later automation taking priority

1. Turn the test light on, trigger capture followed by off, then issue a separate lights-off command from HA.
2. Trigger restore. The test light should remain off because the later command takes priority, even though it was already visibly off.
3. Repeat without the intervening command. Restore should now return the remembered state.
4. For a multi-entity device, test the actual control entity your other automations use. Device-registry grouping is important to the priority behaviour.

### Discard or replace a saved scene

1. Call mungoon_button_restore.clear with the key when the temporary scene should be forgotten.
2. Capturing under an existing key replaces its old snapshot. Restore consumes the snapshot, so pressing restore twice does not repeat an old scene.
3. After HA restart, integration unload or scene reload, take a new capture. Snapshots are held in memory, not a persistent undo history.

## Keep your work

Snapshots exist in HA memory. They are not a database or a cross-restart backup. A failed capture clears an old snapshot and stops the sequence; all requested entities must be available at capture time.

## If something looks wrong

- Restore does nothing: check key spelling, whether the snapshot was already consumed, and whether HA restarted.
- One device stays unchanged: inspect commands issued after capture; it may be intentionally ineligible.
- Single press never runs: check the button’s actual HA events and automation trigger.
- Unavailable entity: fix availability before capture rather than carrying forward an older snapshot.

## What this manual does not promise

Direct changes through a physical remote or vendor application may not produce a HA service event and are not universally tracked. This is targeted restore, not general undo. Eight policy tests passed previously; a clean HA installation has not been rerun for this documentation update.

Screenshots show the actual application where captured. The offline demo is a deliberately smaller simulation and identifies its dummy services. It never controls devices, sends notifications, uploads files or launches printing.
