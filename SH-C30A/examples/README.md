<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30A — Examples

**Every example states which firmware it needs**, because the firmware decides how the host
talks to the adapter. If you are not sure which one you have →
[`docs/identify-firmware.md`](../../docs/identify-firmware.md)

| Example | Firmware | Platform |
|---|---|---|
| [`linux-socketcan.md`](linux-socketcan.md) | candlelight *(as shipped)* | Linux |
| [`python-gsusb.py`](python-gsusb.py) | candlelight *(as shipped)* | Windows *(macOS untested)* |

## Which one do I want

**On Linux, neither of these needs anything installed.** The kernel claims the adapter and
gives you a SocketCAN interface — [`linux-socketcan.md`](linux-socketcan.md) is the whole
story, and Python there means `python-can` with `interface="socketcan"`.

**On Windows** there is no kernel CAN stack, so Python talks to the adapter through libusb.
That is what [`python-gsusb.py`](python-gsusb.py) does, and its header explains the one
install step Windows needs.

Reference for the interface's own arguments:
<https://python-can.readthedocs.io/en/stable/interfaces/gs_usb.html>
