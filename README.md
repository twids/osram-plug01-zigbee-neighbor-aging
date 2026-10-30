# OSRAM Plug 01 Zigbee neighbor aging

Experimental firmware analysis and patch for intermittent Zigbee connectivity on the OSRAM LIGHTIFY Plug 01 / Plug 01. This project documents a reverse-engineered stale-neighbor cleanup defect and a narrowly scoped correction.

**Status: experimental.** A modified image was installed and booted on one physical Plug 01 (OTA version 0x0102050a, Basic build label P1.05.10). The owner later reported improved stability after returning it to its original location, while Home Assistant history still showed multi-hour unavailable periods. This is encouraging, but does not prove the patch caused the improvement or is suitable for every unit.

## Symptom and finding

One sibling-neighbor cleanup path increments a six-bit counter by four, masks it to 0–63, then compares it with 75. The removal branch cannot be reached. The candidate increments by one and compares against 19, preserving adjacent packed flags and a similar count-based delay.

The firmware also contains route discovery and route invalidation paths. This patch does not force a route to a particular device, guarantee a replacement route exists, or prove the defect caused any specific outage.

## Original firmware

The matching Plug 01 firmware 1.2.5.9 can be downloaded from [LEDVANCE's Zigbee firmware endpoint](https://api.update.ledvance.com/v1/zigbee/firmwares/download?Company=4364&Product=39&Version=1.2.5.9). The endpoint returns the OTA file directly. Expected size: 121,680 bytes. Expected SHA-256: c70126e43666f0a83077e8d93c587b7c0cefcd37d4719ebbeab1e33090b7c3b5. Verify it before building. The vendor binary is not mirrored here.

## Contents

- [Patch analysis](docs/patch.md)
- [Build the experimental OTA locally](docs/build.md)
- [Home Assistant ZHA guide](docs/home-assistant.md)
- [Testing and limitations](docs/testing.md)

## Scope and limitations

Only one physical unit has been reported running the modified firmware. Long-term recovery, rollback, UART recovery, certification, and compatibility across Plug 01 variants are unknown. Installation is manual and intended for a single device. Do not enable network-wide automatic installation.

Not affiliated with OSRAM, LEDVANCE, Home Assistant, or the Connectivity Standards Alliance.
