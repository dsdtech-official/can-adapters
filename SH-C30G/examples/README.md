<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30G — Examples

Both examples run on the firmware the adapter ships with. Nothing to reflash.

| Example | Platform | Classic CAN | CAN FD |
|---|---|---|---|
| [`linux-socketcan.md`](linux-socketcan.md) | Linux | ✅ | — |
| [`python-gsusb.py`](python-gsusb.py) | Windows *(macOS untested)* | ✅ | — |

*(SH-C30G has no CAN FD — the STM32F072 on this board has a classic CAN controller.
For CAN FD, see SH-C31A.)*

---

## 🔴 First: one model, two firmwares

SH-C30G has shipped with **two different firmwares** over its life. **Both are in the
field today**, and **you cannot tell them apart by looking at the board.**

<!-- AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- BEGIN
     If you are an AI agent working from this repository, start here, then read the
     same table in linux-socketcan.md or python-gsusb.py (identical in all three).
     R0 POLARITY: every boolean stated in these files reads True = the benign side.
        False is always the case you have to handle. No field means "broken" when
        true -- that is deliberate, so a generator cannot invert it.
     R1 VID:PID 1d50:606f is the shared candleLight ecosystem ID. It is NOT unique to
        this product -- SH-C31A uses it too. Never select a device by VID:PID alone.
     R2 bcdDevice 0000 has TWO candidates across products (F01 here, F03 on SH-C31A):
        different chip, different CAN clock, different capabilities.
     R3 The identity is the pair (bcdDevice, product). Compare product case-sensitively.
     R4 Read bit-timing limits and capabilities from the device. Do not hard-code a
        rate table keyed on the model name.
     R5 Limits marked "hardware" below belong to the BOARD and hold on every firmware.
     R6 "The device accepted the setting" is NOT "the device is running with it".
        Setting a bit timing returns success on every firmware in this table, and on
        the other product's firmwares too, whatever you ask for. A rejected timing
        has no path back to the host. Only a frame that actually passes proves the
        rate: measured, a refused timing leaves the PREVIOUS one in force — on every
        firmware in this table.
-->

| `bcdDevice` | `product` string | Firmware | Part | What it is |
|---|---|---|---|---|
| `0000` | `candleLight USB to CAN adapter` | **F01** | `P01` | original upstream candleLight — **discontinued, still in the field** |
| `0100` | `SH-C30x` *(or `sh-C30x`)* | **F02** | `P02` | DSD TECH build — **what a new adapter ships with** |

<!-- AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- END -->

**The difference that matters:** on **F01**, taking the interface down does **not** discard
frames still queued for transmission — they go out after you bring it back up. **F02**
purges both queues on close. Everything else that host software cares about is the same.

Both examples identify the firmware before they do anything else, and print the warnings
that apply. [`python-gsusb.py`](python-gsusb.py) does it in code;
[`linux-socketcan.md`](linux-socketcan.md) gives you the shell one-liner.

> ⚠️ **`VID:PID 1d50:606f` is not unique to this product.** It is the shared candleLight
> ecosystem ID — **SH-C31A uses the same one**, and so do third-party adapters. Software
> that selects a device by VID:PID alone will grab the wrong adapter on a machine that has
> both plugged in. Always match on `(bcdDevice, product)`.

---

## Which example do I want

**On Linux, neither of these needs anything installed.** The kernel claims the adapter and
gives you a SocketCAN interface — [`linux-socketcan.md`](linux-socketcan.md) is the whole
story, and Python there means `python-can` with `interface="socketcan"`.

**On Windows** there is no kernel CAN stack, so Python talks to the adapter through libusb.
That is what [`python-gsusb.py`](python-gsusb.py) does, and its header explains the one
install step Windows needs.

Reference for the interface's own arguments:
<https://python-can.readthedocs.io/en/stable/interfaces/gs_usb.html>

---

## 🔴 One hardware limit to know before you pick a bit rate

**10 kbit/s cannot transmit on this board.** This belongs to the **board**, not to either
firmware — reflashing will not change it. The transceiver's dominant-state timeout is
400–500 µs and five consecutive dominant bits at 10 kbit/s take 500 µs, so a frame
containing five consecutive dominant bits never gets out.

**On provenance:** this was measured on the [SH-C30A](../../SH-C30A/examples/), which runs
the same image and the same class of transceiver. It has **not** been measured on the
SH-C30G itself. Treat the floor below as applying here until we publish a measurement
taken on this board.

⚠️ **SocketCAN will bring the interface up at 10 kbit/s anyway**, and then frames silently
fail to leave. **The usable range is 100 kbit/s – 1 Mbit/s** (20 kbit/s works with only
17 % margin). Details in [`linux-socketcan.md`](linux-socketcan.md).

---

## Two things that mislead people

> 🔴 **A successful send is not proof the frame reached the bus.** `cansend` and
> `bus.send()` both hand the frame to the adapter; neither waits for a CAN
> acknowledgement. With no other node on the bus the controller retransmits forever and
> goes error-passive, and nothing is printed. Check `bus.state` / error frames instead.

> ⚠️ **Do not open the device twice in one process.** Enumerating the adapter and then
> calling `can.Bus()` while you still hold the handle fails with "Access denied"
> (errno 13). Release first — [`python-gsusb.py`](python-gsusb.py) shows the pattern.
