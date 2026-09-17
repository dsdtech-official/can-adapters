<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31B on Linux — `slcand` + SocketCAN

The adapter enumerates as a USB CDC serial port. `slcand` turns that serial port into a
standard SocketCAN interface, after which every normal tool (`candump`, `cansend`,
`cangen`, python-can's `socketcan` backend, Wireshark) works on it.

> **Is this the right adapter?** If `ls /dev/ttyACM*` shows nothing but `ip link` shows a
> `can0`, you have an **SH-C31A** (gs_usb firmware) — use [`../../SH-C31A/examples/`](../../SH-C31A/examples/)
> instead. The two are the same board with different firmware; the silkscreen says
> `SH-C31A` on both.

## 1. Find the port

```bash
ls -l /dev/serial/by-id/
```

You should see something ending in `-if00`. Using the `by-id` path instead of
`/dev/ttyACM0` means the name does not move when you plug in a second device.

If nothing appears, check that `cdc_acm` loaded:

```bash
dmesg | tail -20
```

## 2. Confirm what you are talking to

Before anything else, ask the firmware to identify itself:

```bash
stty -F /dev/ttyACM0 raw -echo
timeout 2 cat /dev/ttyACM0 &    # start reading FIRST
sleep 0.3
printf 'V\r' > /dev/ttyACM0
wait
```

> **The order matters.** If you send `V` before the reader is running, the answer arrives
> while nothing is listening and you get an empty result — which looks exactly like a
> dead adapter. Start `cat` first, give it a moment, then write.

The reply is one tab-separated line starting with `+`. The fields worth reading:

| Field | Meaning |
|---|---|
| `Clock: 160` | **CAN clock in MHz.** Tools that assume a different clock will put the adapter bus-off. |
| `Channels: 1` | One CAN channel. |
| `Limits: 512,256,128,128,32,32,16,16` | Bit-timing limits: arbitration `brp/seg1/seg2/sjw`, then the data phase. |
| `Slcan: 105` | slcan protocol version 1.05. |

## 3. Bring up the interface

```bash
sudo slcand -o -c -f -s6 /dev/serial/by-id/usb-...-if00 can0
sudo ip link set can0 up
```

`-s6` selects 500 kbit/s. The digit is an index into a table, not a number:

| Flag | Bitrate |
|---|---|
| `-s0` | 10 k |
| `-s1` | 20 k |
| `-s2` | 50 k |
| `-s3` | 100 k |
| `-s4` | 125 k |
| `-s5` | 250 k |
| `-s6` | **500 k** |
| `-s7` | **800 k** |
| `-s8` | 1 M |

> ✅ **On Linux this table matches the adapter.** The kernel's slcan table and this
> firmware agree that `S7` is **800 k**.
>
> 🔴 **python-can's slcan backend does not agree** — it follows the CANable convention
> where `S7` means 750 k. If you drive the serial port through python-can instead of
> `slcand`, asking for `bitrate=750000` silently gives you **800 000**. See
> [`python-slcan.py`](python-slcan.py).

Check it came up:

```bash
ip -details -statistics link show can0
```

> **It will say `bitrate 0`, and that is normal.** With `slcand` the bit timing lives in
> the adapter, not in the kernel — the kernel is only moving text over a serial port and
> genuinely does not know the rate. `bitrate 0` is not a sign that `-s6` failed.
>
> What that command *is* good for is the error counters further down: they move when the
> bus is unhappy, and they are the fastest way to tell "wrong bitrate" from "nothing is
> talking".

## 4. Use it

```bash
# watch traffic
candump can0

# send a standard frame: id 0x123, 8 bytes
cansend can0 123#DEADBEEF00112233

# send an extended-id frame
cansend can0 12345678#0011223344556677

# generate traffic for a quick sanity check
cangen can0 -g 10 -I 42 -L 8
```

## 5. Shut down cleanly

```bash
sudo ip link set can0 down
sudo pkill slcand
```

---

## Things that catch people out

### `slcand` cannot do CAN FD

The Linux slcan driver is a classic-CAN driver. There is no `-s` code for a data-phase
rate and no way to send an FD frame through it, even though **the adapter itself does FD**.

```
$ cansend can0 '123##1DEADBEEF'
CAN interface is not CAN FD capable - sorry.
```

That is the kernel refusing, not the adapter. Verified on a bench: the same frame sent to
a CAN FD-enabled interface on the same machine was accepted, while the `slcand` interface
refused it every time.

For CAN FD, skip `slcand` and drive the serial port directly — see [`canfd.md`](canfd.md).

### The bitrate must be set before the interface goes up

`slcand`'s `-s` flag is sent to the adapter when the link is opened. Changing it after
`ip link set can0 up` does nothing. Bring the interface down, kill `slcand`, and start
again.

### A bitrate mismatch does not look like a bitrate mismatch

If the rest of the bus runs at a different rate, you will see **no frames at all** and a
rising error count in `ip -details -statistics link show can0` — not an error message.
Check `candump` is silent *and* whether the error counters move before assuming the
adapter is faulty.

### 120 Ω termination is not switchable

The `MR` / `Mr` termination commands exist in the slcan protocol but **this hardware does
not implement them** — it answers `\a` (error) to both. Terminate the bus externally.

---

## What was checked on a machine, 2026-09-17

Run on Ubuntu 24.04 (kernel 6.18) against one adapter carrying the current factory
firmware. The peer was a second CAN adapter on the same bus.

| Claim on this page | Result |
|---|---|
| The adapter enumerates as `/dev/ttyACM0` | ✅ |
| The `V` recipe returns the identity line | ✅ **after the ordering fix above** — the original write-then-read form returned nothing |
| `slcand -o -c -f -s6` + `ip link set up` brings the interface up | ✅ |
| `cansend` / `candump` carry traffic | ✅ **5/5 frames each direction** |
| The interface shows `bitrate 0` | ✅ confirmed — expected, see the note above |
| `800000` is in the kernel's slcan rate table | ✅ confirmed by reading the table off the live interface |
| `slcand` refuses CAN FD | ✅ confirmed, with a CAN FD-capable interface on the same machine accepting the same frame as a control |

Not checked: a native Linux machine (this was WSL2), and any bitrate other than 500 k.

## Where these numbers come from

The `V` field values above were read on **one adapter on a bench**, on **2026-08-29**. Your unit will differ in `Serial:` and may differ in `Firmware:`.
`Clock: 160` and `Channels: 1` are properties of this firmware build and hardware, not of
that individual unit.
