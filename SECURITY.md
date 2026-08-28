<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Security policy

## Reporting a vulnerability

Report security issues **privately**, by email to the address on
<https://www.deshide.com>. Please do not open a public issue for one.

Tell us what the issue is, which model and firmware version you saw it on, and how to
reproduce it. We aim to acknowledge within 5 working days.

## Scope

| In scope | Out of scope |
|---|---|
| The firmware images we build and publish in [Releases](../../releases) | Software that merely works with our adapters — SavvyCAN, python-can, cangaroo and the rest. Report those to their own authors |
| Everything in this repository: example code, documentation, hardware design files | Attacks that need physical possession of the adapter |
| Our build and release tooling | Anything about a CAN bus being unauthenticated — see below |

Our firmware is built from **candleLight_fw** and its CAN FD fork; attribution and the full
licence chain are in [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md). A flaw that comes
from upstream is still in scope for us if we ship it — report it here, and we will pass it
on rather than leave you to work out who owns which line.

## What these adapters are, and are not

A CAN adapter is a transparent bridge onto a bus that has **no authentication of any kind**.
That is a property of CAN itself, not of our products: anything on the bus can send any
frame, claim any identifier, and nothing on the bus can tell where a frame came from.

Treat physical access to a CAN bus as full control of that bus. **Do not use the adapter as
a security boundary.** It does not filter, authenticate, rate-limit or log, and it is not
designed to.

The adapter holds no keys and no user data. Its firmware can be replaced over USB by anyone
who can plug into it — that is deliberate, and it is how you flash it.
