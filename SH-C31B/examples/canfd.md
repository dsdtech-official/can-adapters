<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31B — CAN FD

The SH-C31B does CAN FD, but **not through `slcand`**: the Linux slcan driver is a
classic-CAN driver with no data-phase rate and no way to send an FD frame. On every
platform, FD means driving the serial port directly.

The mechanics are small — three extra things on top of [`python-slcan.py`](python-slcan.py).
The traps are the part worth reading.

---

## 🔴 Read this before you put it on a real bus

**Do not use the single-digit `Y` codes on a real CAN FD bus.** They exist, they are easy,
and they will work on your desk between two adapters — which is exactly why they are
dangerous.

The firmware author's own manual says so, in a red box:

> *"Do not use the commands `S` and `Y` for CAN FD. They do not allow to choose the
> correct samplepoint. You can use them to make tests between 2 adapters on your desk,
> but not if you want to connect to a real CAN FD bus."*

The reason is the sample point. The `S`/`Y` codes fix it at 75 % (and `Y8` at 50 %). A
real bus has a sample point chosen for its own topology, and CAN FD is far less forgiving
of a mismatch than classic CAN is — a mismatch that classic frames sail through can put
the FD data phase into error-passive or bus-off.

**On a real bus, set the timing explicitly** with the lowercase forms:

```
s<prescaler>,<seg1>,<seg2>,<sjw>      arbitration phase
y<prescaler>,<seg1>,<seg2>,<sjw>      data phase
```

Compute those from **the clock the adapter reports** (`Clock:` in the `V` reply — it is
**160 MHz**) and the sample point your bus uses. The limits are in the same `V` line:
`Limits: 512,256,128,128,32,32,16,16` — arbitration `brp/seg1/seg2/sjw`, then data.

The `Y` codes below are documented because they are useful on a bench. They are not a
recommendation for a vehicle or a machine.

---

## The three extra things

### 1. Set the data-phase rate **before** opening

If you do not, every FD frame command (`d` `D` `b` `B`) is rejected — the firmware
answers with a "baudrate not set" feedback code, not a frame.

```
S5        arbitration 250 k
Y2        data phase 2 M          <-- this one is easy to forget
O         go on the bus
```

### 2. DLC is a **single hex character**, not a byte count

This catches nearly everyone. In classic CAN the length digit and the byte count are the
same thing up to 8. In FD they are not:

| DLC char | Bytes | | DLC char | Bytes |
|---|---|---|---|---|
| `0`–`8` | 0–8 | | `C` | 24 |
| `9` | 12 | | `D` | 32 |
| `A` | 16 | | `E` | 48 |
| `B` | 20 | | **`F`** | **64** |

So a full 64-byte frame is `F`, not `64` and not `40`.

### 3. Pick the right frame letter

| Letter | Frame |
|---|---|
| `d` | FD, standard id, **no** bit-rate switch |
| `D` | FD, extended id, no BRS |
| `b` | FD, standard id, **with** BRS |
| `B` | FD, extended id, with BRS |

A 64-byte BRS frame to id `0x123`:

```
b123F00112233...   (64 bytes of hex payload)
```

---

## A bench example

```python
# continues from python-slcan.py -- same Adapter class
dev = Adapter("/dev/ttyACM0")        # or "COM7"
info = dev.identify()
assert info["Clock"] == "160"        # bit timings depend on this

dev._cmd("C", expect_reply=False)    # close first. C answers NOTHING on this
                                     # firmware -- see the note below
dev._cmd("S5")                       # arbitration 250 k
dev._cmd("Y2")                       # data phase 2 M   (bench only -- see above)
dev._cmd("OI")                       # OI = internal loopback: nothing reaches
                                     # the wire. Use "O" for the real bus.

payload = bytes(range(64))
dev._cmd("b123F" + "".join("%02X" % b for b in payload))
```

On a real bus, replace `S5` / `Y2` with `s.../y...` computed for that bus, and
open with `O` instead of `OI`.

> ### `C` (close) answers nothing at all
>
> Every other command answers `\r` on success or `\a` on rejection. **`C` answers
> neither** — not when the channel is open, not when it is already closed. Host code
> that waits for a reply to `C` will sit there until its timeout expires every single
> time.
>
> Measured on a real adapter carrying the current factory firmware, on 2026-09-17.

### Reading FD frames back

**`python-slcan.py`'s `recv()` decodes classic frames only.** Handed an FD frame it
returns `None` — the parser accepts `t` `T` `r` `R` and nothing else.

Verified on the bench: through internal loopback, a classic frame came back decoded
correctly while a 64-byte FD frame returned `None`.

If you need to receive FD, extend `_parse_frame()` to accept `d` `D` `b` `B` and to map
the DLC character through the table above. The wire format is otherwise the same.

---

## Rate codes, and why some of them are a trap

Measured on **one adapter on a bench, on 2026-08-29**, sending
64-byte frames against a second adapter over a short link at room temperature:

| Code | Data rate | Bench result |
|---|---|---|
| `Y0` | 500 k | passed — but see "BRS disappears" below |
| `Y1` | 1 M | passed |
| `Y2` | 2 M | passed, 50/50 both directions, no error frames |
| `Y4` | 4 M | passed |
| `Y5` | 5 M | passed, 50/50 both directions, no error frames |
| `Y8` | 8 M | passed on the bench — 🔴 **but it is over spec, see below** |

### 🔴 `Y8` works on a bench and is still wrong

The transceiver on this board is rated **5 Mbaud**. `Y8` is 8 M. It passed 50 frames each
way on a short bench link, and that is not evidence that it is usable — it is evidence
that a short link at room temperature tolerates it. `Y5` is already sitting right at the
limit.

### 🔴 The firmware will not stop you

The build this firmware comes from declares a maximum of **10 Mbaud**, because the same
source serves boards with faster transceivers. On this board the limit is the transceiver,
and the firmware does not know that.

The author was asked about this directly:

> *"you will be allowed to set 10 Mbaud but you will run into Bus Off instead of getting
> an error."*

So the failure mode for an over-spec rate is **bus-off**, not a rejected command. **A
command being accepted is not a statement that the rate is supported.**

### BRS disappears when the two phases are the same rate

If the arbitration rate and the data rate are equal (`S6` + `Y0`, both 500 k), a frame
sent with `b` (BRS) arrives at the far end **without** the BRS flag, and FD frames coming
the other way are reported as `d` rather than `b`.

This reproduced consistently on the bench. We have not established the mechanism.

**Practical consequence:** do not use "the echo came back as `b`" as your check that a
BRS frame was sent.

### Arbitration and data prescalers usually differ

CiA recommends that both phases use the same prescaler. On this firmware most `S`/`Y`
combinations do not — of the pairs checked, only `S4`+`Y1` and `S5` with `Y2`/`Y4`/`Y5`/`Y8`
came out matched. This is another reason to set both phases explicitly on a real bus.

---

## 🔴 Proof that the sample-point warning is real

The warning above is not theoretical. On a bench, with the adapter transmitting onto a
**real bus** (not loopback) and a second adapter receiving:

| Frame sent | Peer at **75 %** (matched) | Peer at **87.5 %** (mismatched) |
|---|---|---|
| 64-byte frame **with BRS** (`b`) | ✅ arrived | 🔴 **lost** |
| 64-byte frame **with BRS** (`b`) | ✅ arrived | 🔴 **lost** |
| 64-byte frame **without BRS** (`d`) | ✅ arrived | ✅ arrived |
| 8-byte classic frame (`t`) | ✅ arrived | ✅ arrived |

Reproduced 3 times. The only thing changed between the two columns was the receiver's
arbitration sample point.

### ⚠️ The consequence is sharper than "FD stops working"

**Classic frames still get through. So do FD frames without BRS.** Only the frames that
switch to the fast data rate are lost.

So if you are checking whether a bus is healthy:

> **Do not conclude the link is good because classic traffic flows.**
> **Do not conclude it because FD frames flow either — send frames _with BRS_.**

A link can carry classic CAN and non-BRS FD perfectly while dropping every BRS frame,
which is exactly the configuration that looks fine on a bench and fails in the field.

*(We have not established the mechanism — the mismatch was in the arbitration phase while
the lost frames are the ones switching to the data phase. Directionally that makes sense;
we did not prove it.)*

## What **was** checked on a board, 2026-09-17

On one adapter running the current factory image. The
first group went through the firmware's own internal loopback so nothing reached a wire;
the sample-point table above was on a real bus against a second adapter.

| Claim on this page | Result |
|---|---|
| An FD frame without a data rate set is rejected | ✅ rejected (`\a`) |
| `S5` → `Y2` → `OI` is accepted in that order | ✅ all three accepted |
| DLC `F` means 64 bytes | ✅ all 64 payload bytes came back intact |
| A `b` frame keeps BRS when the two phases differ | ✅ came back as `b`, not `d` |
| `C` answers nothing | ✅ confirmed, open or closed |
| `recv()` in `python-slcan.py` decodes FD | ❌ returns `None` (classic control frame decoded fine) |

## What has **not** been checked

- **Error-state signalling (ESI)** has not been exercised at all.
- Everything above is a **bench** result on a short link, at the dates given.
- Only one rate pair was exercised: 500 k arbitration with a 2 M data phase.
- The sample-point test used two points (75 % and 87.5 %). We did not sweep the range in
  between, so we cannot tell you where the boundary is — only that 12.5 points apart is
  already enough to lose every BRS frame.
- Results come from a single adapter. They are not a per-unit test report.

Nothing here should be read as "CAN FD has been fully verified on this product".
