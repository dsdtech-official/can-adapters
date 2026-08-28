<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Which firmware is on my adapter?

Our CAN adapters can run either of two firmware personalities. They are **not**
interchangeable at the host end — the software you use depends on which one is loaded.

| | **slcan** | **candlelight** |
|---|---|---|
| Appears as | a serial port | a raw USB device |
| Windows | `COM<n>` in Device Manager, under *Ports* | *Universal Serial Bus devices*, uses WinUSB |
| Linux | `/dev/ttyACM<n>` | claimed by the kernel `gs_usb` driver → a **SocketCAN** interface (`can0`) |
| macOS | `/dev/tty.usbmodem*` | not supported by the kernel; needs userspace software |
| CAN FD | supported when the software opens the serial port directly | not supported |
| Typical software | python-can (`slcan`), cangaroo, SavvyCAN, `slcand` | `can-utils`, SocketCAN, cangaroo, python-can (`gs_usb`) |

## Telling them apart in 10 seconds

**Windows** — open Device Manager:

- A new entry under **Ports (COM & LPT)** → **slcan**
- A new entry under **Universal Serial Bus devices** → **candlelight**

**Linux** — plug the adapter in and run:

```bash
ip link show | grep can        # a "can0" interface appears  → candlelight
ls /dev/ttyACM*                # a /dev/ttyACM<n> appears    → slcan
dmesg | tail -20               # shows which driver claimed it
```

## Confirming the slcan version

With the adapter on a serial port, send `V` followed by a carriage return and read the
reply. Any serial terminal will do:

```bash
# Linux / macOS
stty -F /dev/ttyACM0 raw 115200 && printf 'V\r' > /dev/ttyACM0 && head -c 16 /dev/ttyACM0
```

```python
# Cross-platform, needs pyserial
import serial, time
s = serial.Serial('COM3', 115200, timeout=1)   # or '/dev/ttyACM0'
time.sleep(2)          # python-can waits 2 s after opening; so should you
s.write(b'V\r')
print(s.read(16))
```

> **Some builds do not reply at all.** The upstream CANable firmware has the CR/BEL
> acknowledgement commented out, so a version query can simply time out. A silent adapter
> is not a broken one.

## Changing firmware

Both personalities are flashed over USB DFU. See
your model's firmware folder — [SH-C30A](../SH-C30A/firmware/).
