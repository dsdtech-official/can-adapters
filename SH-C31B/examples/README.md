<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31B — Examples

The SH-C31B ships with **slcan firmware** and appears as a **plain serial port**.
Nothing to install on Windows, nothing to reflash.

| Example | Platform | Classic CAN | CAN FD |
|---|---|---|---|
| [`linux-slcand.md`](linux-slcand.md) | Linux | ✅ | — *(see below)* |
| [`python-slcan.py`](python-slcan.py) | Windows + Linux + macOS | ✅ | — |
| [`canfd.md`](canfd.md) | Windows + Linux + macOS | — | ✅ |

---

> ## 🔴 First: is this actually an SH-C31B?
>
> **The silkscreen on the board says `SH-C31A`.** That is not a mistake and not a
> mislabelled unit — SH-C31A and SH-C31B are **the same board**. The name describes
> **which firmware was installed at the factory**, nothing else.
>
> **So you cannot identify it by looking at it.** Plug it in and look at what appears:
>
> | What the computer sees | What you have | Which examples |
> |---|---|---|
> | **A serial port** (`COMx` on Windows, `/dev/ttyACM0` on Linux) | **SH-C31B** — slcan firmware | **this folder** |
> | **A CAN network device** (USB `1D50:606F`) | **SH-C31A** — gs_usb firmware | [`../../SH-C31A/examples/`](../../SH-C31A/examples/) |
>
> Both are supported products. They just speak completely different protocols over USB,
> and **no example here works on the other one**.

## Confirm it with one command

Send `V\r` to the serial port. It answers with a single tab-separated line, e.g.:

```
+Board: Multiboard   MCU: STM32G431   DevID: 1128   Firmware: ...
Slcan: 105   Clock: 160   Channels: 1   Quartz: No
Limits: 512,256,128,128,32,32,16,16   HAL: 1.2.5   Serial: ...
```

`V` is the single most useful command on this firmware — it gives you the clock, the
channel count and the bit-timing limits without any guessing.

> **`Board:` and `MCU:` are compile-time strings, not hardware readings.** Do not use
> `Board: Multiboard` to recognise a DSD TECH product. `DevID` is a real register read.

---

## Three things that will bite you

These are the ones that cause silent wrong behaviour rather than an error message.
Each example repeats the ones relevant to it.

### 1. `S7` is **800 kbit/s**, not 750 k

The single-digit `S` codes are not a standard — different firmwares assign different
rates to the same digit. On this adapter `S7` is **800 000**, which matches the LAWICEL
original, the Linux kernel, USBtin and most other implementations.

🔴 **The trap is python-can.** Its slcan backend follows the CANable convention where
`S7` means 750 k, so:

| You ask python-can for | It sends | The adapter actually runs at |
|---|---|---|
| `bitrate=750000` | `S7` | 🔴 **800 000** — silently 6.7 % off, **neither side reports anything** |
| `bitrate=800000` | — | ⛔ rejected as an invalid bitrate |

**If you need 800 k, send `S7` yourself instead of going through `bitrate=`.**
`slcand` on Linux does *not* have this problem — the kernel's table also says 800 k.

### 2. The CAN clock is **160 MHz**

Host software that assumes a fixed clock (many tools assume 48 MHz or 80 MHz) will
compute bit timings that do not match this adapter. The failure is **not** "slightly off
frequency" — the adapter goes **bus-off** and transmits nothing.

Read `Clock:` from `V` rather than assuming.

### 3. Leave `MF` alone on a production path

`MF` turns on command-execution feedback. Once it is on, **every reply gains a leading
`#`**: `\r` becomes `#\r`. A host that only accepts `\r` will fail to parse.

The default is off and safe. `Mf` turns it back off.

---

## About CAN FD

This adapter does CAN FD, but **not through `slcand`** — the Linux slcan driver is a
classic-CAN driver. For FD, drive the serial port directly; see [`canfd.md`](canfd.md).

⚠️ FD also has its own sharp edge that has nothing to do with this adapter being ours:
the single-digit `Y` rate codes **must not be used on a real CAN FD bus**, only on a
bench between two adapters. `canfd.md` explains what to use instead.

---

## Scope of what is written here

Measured figures in these files were taken on **one adapter on a bench**, at the dates
given next to each result. They are not a per-unit test report and not a statement
about every unit.

Some FD behaviour (error-state signalling in particular) has **not** been exercised, so
nothing here should be read as "CAN FD has been fully verified".
