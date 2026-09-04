<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Other firmware — ElmueSoft CANable 2.5

The **SH-C31A** and **SH-C31G** ship with our own gs_usb build. They will also run
**ElmueSoft's CANable 2.5 firmware**, which is a separate project by a different author,
and we publish it here so you can choose.

> ### With thanks to Elmue
>
> **The DSD TECH team is very grateful to Elmue for this work.** CANable 2.5 is his own
> project, written and maintained by him, and he made it work across a range of boards from
> different manufacturers — including ours. The `Multiboard` builds on this page exist
> because he took the trouble to support hardware that has no crystal fitted, which is what
> our SH-C31A and SH-C31G are.
>
> His work is his own. Nothing on this page should be read as him endorsing us or our
> products.

## Which one do I want?

Both are built from the same source at the same version. They differ in **how the adapter
talks to your computer**, and that decides which software can use it.

| | **Candlelight 2.5** | **Slcan 2.5** |
|---|---|---|
| Host interface | Raw USB (`gs_usb` / WinUSB) | **CDC virtual serial port** |
| Windows driver | WinUSB | **None — it appears as a COM port** |
| Linux | SocketCAN via the kernel `gs_usb` driver | SocketCAN via `slcand`, or any serial tool |
| CAN FD | ✅ | ✅ |
| Closest to what we ship | ✅ same class of interface | ❌ different class entirely |
| Details | [`elmue-candlelight-2.5.md`](elmue-candlelight-2.5.md) | [`elmue-slcan-2.5.md`](elmue-slcan-2.5.md) |

**If you are happy with the firmware the adapter came with, you do not need either of
these.** Our own build is what we test, what we support, and what every measurement on the
model pages was taken on.

**Reasons people do want one of them:**

- **Slcan 2.5** puts the adapter on a plain COM port. If your software wants a serial
  port, or you would rather not deal with WinUSB at all, this is the one.
- **Candlelight 2.5** adds features our build does not have — `GET_STATE`, bus load
  reporting, filter and pin control, flash read/write — through Elmue's own extensions to
  the protocol.

## Software: the author's own application

**If you flash this firmware, [HUD ECU Hacker](https://netcult.ch/elmue/HUD%20ECU%20Hacker/)
is the application it was written alongside — we recommend it.** Elmue wrote CANable 2.5
while adding CANable support to that program, and his documentation says it supports the new
firmware's features in full.

It can also **install this firmware for you**: it carries a built-in CANable firmware
updater, and using that is what he recommends over flashing by hand.

| | |
|---|---|
| What it is | ECU diagnostics and tuning, with a built-in CAN bus debugger, logger and terminal |
| Protocols | CAN Raw, ISO 15765, **J1939** (8 500 parameters), **NMEA 2000** (3 000 parameters), K-Line (ISO 9141, ISO 14230, KW1281, Honda) |
| Platform | **Windows only** — 7, 8, 10 and 11. Not Linux |
| Price | **Charityware** — he asks for a donation to a non-profit of your choice, not to himself |
| Source | Closed |
| Where | <https://netcult.ch/elmue/HUD%20ECU%20Hacker/> |

**We link rather than bundle it, and the capabilities listed above are his description
rather than our measurements.** Questions about it go to him, the same as for the firmware.

> **On Linux you need none of this.** The Candlelight build comes up as a SocketCAN
> interface through the kernel `gs_usb` driver, and the Slcan build through `slcand` — then
> `can-utils`, `python-can` or anything else that speaks SocketCAN.

## Download

Both files are attached to a single release here, and both are **byte-for-byte the files
Elmue publishes**, taken from a pinned commit:

**[ElmueSoft CANable 2.5](https://github.com/dsdtech-official/can-adapters/releases/tag/SH-C31A/elmue-2.5)**

| File | For | SHA-256 |
|---|---|---|
| `STM32G431-Candlelight2.5-Multiboard.dfu` | gs_usb / WinUSB | `7adae1c1…4561d7` |
| `STM32G431-Slcan2.5-Multiboard.dfu` | CDC serial port | `8fb57b07…43e7f59` |
| `SHA256SUMS.txt` | checksums for both | — |
| `THIRD-PARTY-NOTICES.md` | **the MIT notice. Carry it if you mirror these** | — |

```bash
sha256sum -c SHA256SUMS.txt
```

### Where these came from, exactly

| | |
|---|---|
| Upstream | <https://github.com/Elmue/CANable-2.5-firmware-Slcan-and-Candlelight> |
| Pinned commit | [`e862f6a6`](https://github.com/Elmue/CANable-2.5-firmware-Slcan-and-Candlelight/commit/e862f6a6b609ddee22d071e439ebaee1a52010ff) |
| Author's page | <https://netcult.ch/elmue/CANable%20Firmware%20Update> |

> ℹ️ **We renamed the two files.** Upstream calls them
> `STM32G431 - Candlelight2.5 - Multiboard.dfu` and `STM32G431 - Slcan2.5 - Multiboard.dfu`,
> with spaces. GitHub replaces spaces in release assets with periods, which would break
> `sha256sum -c`, so ours use hyphens instead. **The contents are untouched** — the
> checksums above are of the upstream files exactly as published.

**We pin a commit rather than linking a branch,** because a branch moves and what we
publish is the build we actually put on a board. We verified that the files in the release
above are identical to that commit — same SHA-256, same byte count.

> ⚠️ **Upstream ships 16 different `.dfu` files.** They are for different boards and
> different clock configurations. **Take exactly the two named above** — the `Multiboard`
> ones. Flashing a variant built for a 25 MHz crystal onto a board that has none will not
> work, and the failure is not obvious.

> ⚠️ **Newer versions may exist upstream.** We pin this one because it is the one we tested.
> If Elmue publishes a newer build, it will be on his repository before it is here.

## Flashing

Same procedure as our own firmware — USB DFU to the STM32 system bootloader (`0483:DF11`).
The **BOOT** position of the on-board switch puts the MCU there. A USB cable is all you
need.

### Going back

**Nothing here is one-way.** Our own build is on the model's firmware page
([SH-C31A](../SH-C31A/firmware/README.md#download) ·
[SH-C31G](../SH-C31G/firmware/README.md)) and flashes exactly the same way. The bootloader
lives in ROM and is not touched by any of this.

## What we support, and what we do not

**We did not write this firmware, we do not maintain it, and we cannot rebuild it** — what
we publish is the author's own precompiled file, not something we compiled ourselves.

| | |
|---|---|
| **Hardware faults** | ✅ Ours. Warranty is unaffected by which firmware you run |
| **Getting back to our firmware** | ✅ Ours — ask us |
| **Bugs in CANable 2.5** | ⛔ Report upstream: <https://github.com/Elmue/CANable-2.5-firmware-Slcan-and-Candlelight/issues> |
| **Feature requests for CANable 2.5** | ⛔ Upstream. It is his project |

**Please do not send Elmue support requests about our hardware, and please do not send us
feature requests about his firmware.** Each of us can only fix our own half.

## Licence

The firmware source carries **the MIT licence**:

```
The MIT License
Copyright (c) 2025 ElmueSoft / Nakanishi Kiyomaro / Normadotcom
https://netcult.ch/elmue/CANable Firmware Update
```

MIT permits redistribution in source or binary form **provided that notice travels with
it**, which is why [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md) is attached to the
release. **If you mirror these images anywhere, carry that file with them.**

> Note that the copyright is held by **three** parties, not one. The sample applications in
> the same upstream repository are under a **different** licence (BSD-3-Clause) — if you use
> those as well, read their own `License.txt`.
