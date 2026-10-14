# HA Button Restore: start here

**Continuing this tool? Read [the detailed handover](HANDOVER.md).** For pictures and operation, use the [manual](USER-MANUAL.md) and [offline demo](../demo.html).

Capture a device group before a temporary action, then restore only devices not claimed by a newer HA command. A later OFF command takes priority even when the visible state was already OFF.

**Start with:** Understand the sequence. Suppose a lamp is on. A single press captures that state, then switches the lamp off for a temporary scene.

**Source:** this is a private source checkpoint, not a live-system mirror. Check [the source manifest](../SOURCE-MANIFEST.json) and current working files before merging.

**Keep your work safe:** Snapshots exist in HA memory. They are not a database or a cross-restart backup. A failed capture clears an old snapshot and stops the sequence; all requested entities must be available at capture time.

**Next maintainer action:** Test capture→off→restore and capture→off→newer off→restore on a spare entity, including another entity of the same physical device. Check compatibility with the target HA version; vendor-app/remote changes may not emit tracked HA commands.

**Status:** private upload verified on 14 October 2026. These guides accompany the source package. Live runtime, data backups and full recovery were not retested. Public sharing was authorised on 14 October 2026; the NAS backup remains private.
