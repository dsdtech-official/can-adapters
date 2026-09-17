<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30L — Examples

Everything here runs on the firmware the adapter already has. Nothing to reflash.

| File | Platform | For |
|---|---|---|
| [`linux-socketcan.md`](linux-socketcan.md) | Linux | both firmwares — the kernel handles the difference |
| [`python-gsusb.py`](python-gsusb.py) | Windows | the firmware a **new** adapter ships with |
| [`python-gsusb-legacy.py`](python-gsusb-legacy.py) | Windows | adapters made **before September 2026** |

*(SH-C30L has no CAN FD — the STM32F072 on this board has a classic CAN controller.
For CAN FD, see SH-C31A.)*

---

## Which of the two Windows files do I want?

**Plug the adapter in and look at the name it reports.** Device Manager on Windows, or:

```bash
lsusb -v -d 1d50:606f | grep -E 'iProduct|bcdDevice'
```

| It says | You want |
|---|---|
| **`SH-C30x`** *(or `sh-C30x`)* | [`python-gsusb.py`](python-gsusb.py) |
| **`candleLight USB to CAN adapter`** | [`python-gsusb-legacy.py`](python-gsusb-legacy.py) |

**You do not have to get this right first.** Either script checks before it opens
anything, and if you picked the wrong one it says so and stops.

> ⚠️ **`VID:PID 1d50:606f` is not unique to this product.** It is the shared candleLight
> ecosystem ID — **SH-C31A uses the same one**, and so do third-party adapters. Anything
> that selects a device by VID:PID alone will grab the wrong adapter on a machine with
> both plugged in. Match on the **product string**.

---

## What is actually different between the two

Only one thing changes what your program has to do:

> 🔴 **On the older firmware, closing the channel does not discard frames still queued
> for transmission.** They go out after you open it again — possibly minutes later, into
> whatever bus you are attached to by then. **Drain before you close.**
> The current firmware purges both queues on close.

Two smaller ones: the older firmware **lights neither LED** (not a fault), and it holds
**30** frames in flight rather than 31 — both measured.

> ⚠️ **That ceiling follows the firmware, not the board.** Same chip, same clock, two
> different numbers. ⛔ **Do not derive one from "it is an SH-C30L".** If you write a bulk
> sender, keep no more than **30** frames outstanding and it holds on either firmware;
> push past the ceiling and you lose frames, sometimes without any error at all.

**Everything else host software touches is the same** — same chip, same 48 MHz CAN clock,
same bit rates, same 32-byte bulk endpoint. Both firmwares honour `listen-only`.

<!-- AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- BEGIN
     This directory's single authoritative table. The two .py files each target ONE
     row and say so; do not reconstruct this table from them.

     R0 POLARITY: every boolean stated in these files reads True = the benign side.
        False is always the case you have to handle. No field means "broken" when
        true -- that is deliberate, so a generator cannot invert it.
     R1 VID:PID 1d50:606f is the shared candleLight ecosystem ID. It is NOT unique to
        this product -- SH-C31A uses it too. Never select a device by VID:PID alone.
     R2 bcdDevice 0000 has TWO candidates across products: the older firmware of
        this board, and the older firmware of the SH-C31A. Different chip,
        different CAN clock, different capabilities. bcdDevice alone is not enough.
     R3 The identity is the pair (bcdDevice, product). Compare product case-sensitively.
        bcdDevice is a valid key only for firmware WE build. Third-party firmware
        stamps its build version there and it moves on every release.
     R4 Read bit-timing limits and capabilities from the device. Do not hard-code a
        rate table keyed on the model name.
     R5 Limits marked "hardware" below belong to the BOARD and hold on every firmware.
     R6 "The device accepted the setting" is NOT "the device is running with it".
        Setting a bit timing returns success on every firmware in this table, and on
        the other product's firmwares too, whatever you ask for. A rejected timing
        has no path back to the host. Only a frame that actually passes proves the
        rate: measured, a refused timing leaves the PREVIOUS one in force.

     | bcdDevice | product                         | manufacturer | firmware | file
     | 0100      | SH-C30x (or sh-C30x)            | DSD TECH     | current  | python-gsusb.py
     | 0000      | candleLight USB to CAN adapter  | bytewerk     | older    | python-gsusb-legacy.py
     | 0000      | canable2 gs_usb                 | canable.io   | NOT THIS PRODUCT -- SH-C31A
     | 0200      | SH-C31x                         | DSD TECH     | NOT THIS PRODUCT -- SH-C31A

     current: close_reopen_flushes_tx=True, listen_only_honoured=True,
              echo_is_trustworthy=True, max_frames_in_flight=31
     older:   close_reopen_flushes_tx=False, listen_only_honoured=True,
              echo_is_trustworthy=True, max_frames_in_flight=30 (measured)
     both:    fclk_can_hz=48000000, bulk_endpoint_bytes=32, supports_can_fd=False,
              min_usable_bitrate=20000 (hardware, see below)
-->
<!-- AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- END -->

---

## Linux or Windows?

**On Linux, nothing needs installing.** The kernel claims the adapter and gives you a
SocketCAN interface — [`linux-socketcan.md`](linux-socketcan.md) is the whole story, and
Python there means `python-can` with `interface="socketcan"`.

**On Windows** there is no kernel CAN stack, so Python talks to the adapter through
libusb. That is what the two `.py` files do; each one's header has the install step.

Reference for the interface's own arguments:
<https://python-can.readthedocs.io/en/stable/interfaces/gs_usb.html>

---

## 🔴 One hardware limit to know before you pick a bit rate

**10 kbit/s cannot transmit on this board.** This belongs to the **board**, not to either
firmware — reflashing will not change it. The transceiver's dominant-state timeout is
400–500 µs and five consecutive dominant bits at 10 kbit/s take 500 µs, so a frame
containing five consecutive dominant bits never gets out. Reproduced across three
firmwares, two boards and two independent implementations.

> **On provenance:** this was measured on the [SH-C30A](../../SH-C30A/examples/), which
> runs the same image. **It has not been measured on the SH-C30L itself**, whose
> transceiver is an equivalent part from a different vendor. Treat the floor below as
> applying here until we publish a measurement taken on this board — and note which way
> that cuts: if this board turns out to manage 10 kbit/s, we are understating it.

⚠️ **SocketCAN will bring the interface up at 10 kbit/s anyway**, and then frames silently
fail to leave. There is no error to tell you why.

| Rate | |
|---|---|
| 5 kbit/s | ⛔ do not use — worse than 10 k by the same mechanism |
| **10 kbit/s** | 🔴 **opens but cannot transmit** |
| 20 kbit/s | ⚠️ works, but only **17 %** margin against the transceiver's timeout |
| **100 kbit/s – 1 Mbit/s** | ✅ the usable range |

---

## Which bit rates python-can can open on Windows

Its `gs_usb` backend solves the bit timing itself, strictly: `f_clock / bitrate` has to
factor into `brp × nbt` with `brp ≤ 32` and `nbt` in 8..25, at a fixed 87.5 % sample
point. This board reports `f_clock = 48 MHz`.

**Eight rates open, all measured on real hardware, both firmwares, 20 frames each way
against a second adapter on the same bus:**

| Rate | `brp` | sample point |
|---|---|---|
| 83.333 k | 32 | 88.89 % ⚠️ |
| 100 k | 30 | 87.50 % |
| 125 k | 24 | 87.50 % |
| 250 k | 12 | 87.50 % |
| 500 k | 6 | 87.50 % |
| 750 k | 4 | 87.50 % |
| 800 k | 4 | 86.67 % ⚠️ |
| 1 M | 3 | 87.50 % |

Refused before the device is even touched, with `ValueError: No suitable bit timings
found.` — 5 k, 10 k, 20 k, 25 k, 30 k, 33.333 k, 40 k, 50 k, 62.5 k, 75 k. **The adapter
supports them; this is the host library's solver.** Use SocketCAN on Linux for those.

> ⚠️ **Two of the eight are not at 87.5 %.** If you share a bus with nodes configured
> elsewhere, check that both ends agree on the sample point.

> ⛔ **Do not carry this table to our other product.** 800 kbit/s opens here because the
> clock is 48 MHz (`48e6/800e3 = 60 = 4 × 15`); on the SH-C31A's 170 MHz clock it cannot
> (`212.5`, not even an integer).

---

## Two things that mislead people

> 🔴 **A successful send is not proof the frame reached the bus.** `cansend` and
> `bus.send()` both hand the frame to the adapter; neither waits for a CAN
> acknowledgement. With no other node on the bus the controller retransmits forever and
> goes error-passive, and nothing is printed. Check `bus.state` / error frames instead.

> ⚠️ **Do not open the device twice in one process.** Enumerating the adapter and then
> calling `can.Bus()` while you still hold the handle fails with "Access denied"
> (errno 13). Release first — both `.py` files show the pattern.
