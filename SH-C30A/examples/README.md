<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30A — Examples

**Every example states which firmware it needs**, because the firmware decides how the host
talks to the adapter. If you are not sure which one you have →
[`docs/identify-firmware.md`](../../docs/identify-firmware.md)

| Example | Firmware | Platform |
|---|---|---|
| [`linux-socketcan.md`](linux-socketcan.md) | candlelight *(as shipped)* | Linux |
| [`python-slcan.py`](python-slcan.py) | slcan | Windows, Linux, macOS |

## gs_usb from Python

For candlelight adapters from Python on Windows, use `python-can`'s `gs_usb` interface.
We are not reproducing its arguments here because they have changed between versions —
take them from the current documentation:
<https://python-can.readthedocs.io/en/stable/interfaces/gs_usb.html>

On Linux you do not need it: the kernel claims the device and you get SocketCAN, which is
what [`linux-socketcan.md`](linux-socketcan.md) covers.
