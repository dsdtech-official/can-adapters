<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31G — Examples

Everything here runs on the firmware the adapter already has. Nothing to reflash.

| File | Platform | For |
|---|---|---|
| [`linux-socketcan.md`](linux-socketcan.md) | Linux | both firmwares · **the only route here that carries CAN FD** |
| [`python-gsusb.py`](python-gsusb.py) | Windows | the firmware a **new** adapter ships with · classic CAN |
| [`python-gsusb-legacy.py`](python-gsusb-legacy.py) | Windows | adapters made **before September 2026** · classic CAN |

---

## 🔴🔴 Which firmware do I have? Check before you join a bus you care about

**Plug the adapter in and look at the name it reports.** Device Manager on Windows, or:

```bash
lsusb -v -d 1d50:606f | grep -E 'iProduct|bcdDevice'
```

| It says | You want |
|---|---|
| **`SH-C31x`** | [`python-gsusb.py`](python-gsusb.py) |
| **`canable2 gs_usb`** | [`python-gsusb-legacy.py`](python-gsusb-legacy.py) |

**You do not have to get this right first.** Either script checks before it opens anything,
and if you picked the wrong one it says so and stops.

> 🔴🔴 **This is not cosmetic, and one difference is a safety problem.**
> The older firmware **reports `listen-only` support and does not honour it.** Ask it to
> stay silent and it still transmits and still acknowledges — no error, no warning. On a
> vehicle or a customer's machine that means you believe you are passive while you are
> interfering. **Identify first.**
>
> **An RX LED that never lights while traffic is clearly arriving is a strong hint you are
> holding the older one.**

### You have the older one? We recommend updating

**The current firmware is a free download, and the upgrade is reversible** — the bootloader
lives in ROM and cannot be overwritten. → [`../firmware/`](../firmware/) for the procedure,
or straight to the **[firmware v1.4
release](https://github.com/dsdtech-official/can-adapters/releases/tag/SH-C31A/fw-v1.4)**
— one build serves both boards in this pair, so the tag carries only one of the two names.

**What you gain:** `listen-only` that actually silences the adapter, echoes you can trust,
and **CAN FD to 5 Mbit/s** — which the older build does not offer at all.

**What changes in the other direction**, so you are not surprised: the current firmware
does **not** discard queued frames when you close the channel, so drain before you close.
And `bcdDevice` moves from `REV_0000` to `REV_0200`, so anything matching on the revision
string needs updating.

---

## What is different

| | **older** (`canable2 gs_usb`) | **current** (`SH-C31x`) |
|---|---|---|
| **`listen-only` / `loopback`** | 🔴🔴 **reported but NOT honoured** — transmits and acknowledges anyway | ✅ honoured, verified against a witness node |
| **Echo frames** | 🔴 **not trustworthy** — measured: ten frames pushed while the channel was closed produced **ten echoes and zero frames on the wire** | ✅ trustworthy |
| **CAN FD** | ✗ **not reported** → the kernel refuses `fd on` outright | ✅ **to 5 Mbit/s** |
| Closing and reopening the channel | discards queued frames | 🔴 **does not** — leftovers go out after the next open. **Drain before you close** |
| RX LED | 🔴 never lights (it drives a pin not connected on this board) | ✅ blinks |
| Bulk endpoint | 32 bytes | **64 bytes** |
| Frames in flight | 30 *(inherited from the current firmware, which shares the same single receive buffer structure — **not measured on this one**)* | **30** (measured) |
| CAN clock | 170 MHz | 170 MHz — ⚠️ **identical, useless for telling them apart** |

> ⚠️ **`VID:PID 1d50:606f` is not unique to this product.** It is the shared candleLight
> ecosystem ID — **SH-C30A uses the same one**, and so do third-party adapters. Anything
> that selects a device by VID:PID alone will grab the wrong adapter on a machine with
> both plugged in. Match on the **product string**.

<!-- AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- BEGIN
     This directory's single authoritative table. The two .py files each target ONE
     row and say so; do not reconstruct this table from them.

     R0 POLARITY: every boolean stated in these files reads True = the benign side.
        False is always the case you have to handle. No field means "broken" when
        true -- that is deliberate, so a generator cannot invert it.
     R1 VID:PID 1d50:606f is the shared candleLight ecosystem ID. It is NOT unique to
        this product -- SH-C30A uses it too. Never select a device by VID:PID alone.
     R2 bcdDevice 0000 has TWO candidates across products: the older firmware of
        this board, and the older firmware of the SH-C30A. Different chip,
        different CAN clock, different capabilities. bcdDevice alone is not enough.
     R3 The identity is the pair (bcdDevice, product). Compare product case-sensitively.
        bcdDevice is a valid key only for firmware WE build. Third-party firmware
        stamps its build version there and it moves on every release.
     R4 Read bit-timing limits and capabilities from the device. Do not hard-code a
        rate table keyed on the model name. Both firmwares here report the SAME CAN
        clock (170 MHz) and the same limits, so the clock cannot separate them.
     R5 "The device reports the capability" is NOT "the capability works". The older
        firmware reports listen-only and loopback and honours NEITHER. Treat the
        _honoured values below as the authority, never the capability word.
     R6 "The device accepted the setting" is NOT "the device is running with it".
        Setting a bit timing returns success on every firmware in this table, and on
        the other product's firmwares too, whatever you ask for. A rejected timing
        has no path back to the host. Only a frame that actually passes proves the
        rate: measured, a refused timing leaves the PREVIOUS one in force.

     | bcdDevice | product          | manufacturer | firmware | file
     | 0200      | SH-C31x          | DSD TECH     | current  | python-gsusb.py
     | 0000      | canable2 gs_usb  | canable.io   | older    | python-gsusb-legacy.py
     | 0000      | candleLight USB to CAN adapter | bytewerk   | NOT THIS PRODUCT -- SH-C30A
     | 0100      | SH-C30x (or sh-C30x)          | DSD TECH   | NOT THIS PRODUCT -- SH-C30A

     current: listen_only_honoured=True, loopback_honoured=True,
              echo_is_trustworthy=True, close_reopen_flushes_tx=False,
              supports_can_fd=True, bulk_endpoint_bytes=64,
              max_frames_in_flight=30 (measured), capability_word=0x000005FB
     older:   listen_only_honoured=False, loopback_honoured=False,
              echo_is_trustworthy=False, close_reopen_flushes_tx=True,
              supports_can_fd=False, bulk_endpoint_bytes=32,
              max_frames_in_flight=30 (inherited, NOT measured),
              capability_word=0x000000F3
     both:    fclk_can_hz=170000000, min_usable_bitrate=5000
-->
<!-- AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- END -->

---

## Linux or Windows?

**On Linux, nothing needs installing.** The kernel claims the adapter and gives you a
SocketCAN interface — [`linux-socketcan.md`](linux-socketcan.md) is the whole story, and
Python there means `python-can` with `interface="socketcan"`.

**On Windows** there is no kernel CAN stack, so Python talks to the adapter through libusb.
That is what the two `.py` files do; each one's header has the install step.
**They carry classic CAN.**

Reference for the interface's own arguments:
<https://python-can.readthedocs.io/en/stable/interfaces/gs_usb.html>

---

## CAN FD

**CAN FD works on the firmware this adapter ships with** — no reflashing, no second
firmware, no serial port. Rated to **5 Mbit/s**, the transceiver's ceiling.
[`../firmware/`](../firmware/) has the full rate table.

> **On provenance:** the per-rate sweep was run on an **SH-C31A** — same microcontroller,
> same image, but **no isolation in the signal path**. What has been run on the SH-C31G
> itself is CAN FD with the isolation in circuit, including an extended soak. Every part
> in this board's signal path is rated for 5 Mbit/s: the digital isolator is a 10 Mbit/s
> part and the **TJA1051T/3** transceiver has its fast-phase timing guaranteed to
> 5 Mbit/s. We will publish a sweep taken on this board when we have one.
*(On the older firmware there is no CAN FD at all — the kernel refuses `fd on`.)*

**Use Linux for it.** We have exercised CAN FD over SocketCAN, and only there.

> 🔴 **Read the rate back after you set it.** `ip link set ... up` exits `0` even when the
> divisors could not reach the rate you asked for — a 4 Mbit/s request lands on
> **3 953 488** without a word of complaint. The same applies to a nominal 800 kbit/s on
> this board's 170 MHz clock. See [`linux-socketcan.md`](linux-socketcan.md).

> 🔴 **Mismatched data-phase sample points are the FD failure you will actually hit.**
> Measured: 12 percentage points apart gave **0 of 50** FD frames and an error-passive
> receiver — while **classic frames over the same wiring went 50 of 50**.
> ⛔ **So never use classic traffic to prove the bus is healthy before blaming CAN FD.**

---

## Which bit rates python-can can open on Windows

Its `gs_usb` backend solves the bit timing itself, strictly: `f_clock / bitrate` has to
factor into `brp × nbt` with `brp ≤ 32` and `nbt` in 8..25. This board runs a **170 MHz**
CAN clock, and that leaves very little:

**Measured — 18 rates tried on real hardware against a second adapter on the same bus.
Only `500000` and `1000000` open, and both pass 20 frames each way.** The other sixteen
(5 k, 10 k, 20 k, 25 k, 30 k, 33.333 k, 40 k, 50 k, 62.5 k, 75 k, 83.333 k, 100 k, 125 k,
250 k, 750 k, 800 k) are refused by the host library before the device is touched.

**The adapter carries 10 k, 125 k and 250 k perfectly well from SocketCAN**, all measured
at 0.0000 % loss. ⛔ **The limit is the host library's solver, not the board.**

> ⛔ **Do not carry this list to our other product.** 800 kbit/s opens on an SH-C30A,
> whose clock is 48 MHz (`48e6/800e3 = 60 = 4 × 15`), and cannot open here
> (`170e6/800e3 = 212.5`, not even an integer). Same library, different arithmetic.

---

## Three things that mislead people

> 🔴 **A successful send is not proof the frame reached the bus.** `cansend` and
> `bus.send()` both hand the frame to the adapter; neither waits for a CAN
> acknowledgement. With no other node the controller retransmits forever and goes
> error-passive, and nothing is printed. Check `bus.state` / error frames instead —
> and on the older firmware, **an echo is not proof either**.

> ⚠️ **There is a limit on frames in flight: 30.** Push more unacknowledged frames at the
> adapter than its pool holds and the extra ones are lost — usually with no overflow bit
> and no error frame at all. Any bulk sender has to respect it.

> ⚠️ **Do not open the device twice in one process.** Enumerating the adapter and then
> calling `can.Bus()` while you still hold the handle fails with "Access denied"
> (errno 13). Release first — both `.py` files show the pattern.
