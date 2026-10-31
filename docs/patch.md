# Patch analysis

## Target image

OSRAM Plug 01 OTA identity: manufacturer 0x110c, image type 0x0027, original version 0x01020509. The application is analyzed as Cortex-M3 Thumb; physical silicon identification was not verified.

## Unreachable cleanup branch

At application address 0x10b812, one sibling-neighbor aging path updates a packed 16-bit field. It increments the six-bit field in bits 7–12 by four, masks it to 0–63, then compares against 75. A six-bit unsigned field ranges only from 0 through 63, so the removal branch cannot be taken. The original +4 sequence also wraps from 60 to 0.

The patch changes two instructions:

| App address | OTA offset | Original | Patched | Effect |
|---|---:|---|---|---|
| 0x10b82e | 0xb88c | 01 f5 00 71 | 01 f1 80 01 | Increment the six-bit field by one |
| 0x10b840 | 0xb89e | 4b 29 | 13 29 | Compare against 19 |

The threshold 19 is ceil(75/4), preserving roughly the call count implied by the original scaling while making the six-bit comparison reachable. Vendor intent and absolute timing are unknown.

## Classic A60 W clear

The vendor image for manufacturer `0x110c`, image type `0x0013`, version `0x01020510` has the same 56-byte function at application address `0x10be76` (OTA offset `0xbed4`). Its two corresponding substitutions are:

| App address | OTA offset | Original | Patched |
|---|---:|---|---|
| `0x10be92` | `0xbef0` | `01 f5 00 71` | `01 f1 80 01` |
| `0x10bea4` | `0xbf02` | `4b 29` | `13 29` |

The A60 trial also updates its own version fields, fixed-length build label, and integrity values. These are separate image layouts; applying Plug 01 offsets or its OTA file to a bulb is incorrect. Matching product and firmware identifiers do not prove a physical unit's entire flash matches the vendor file byte for byte.

## Interpretation

This is a concrete defect in one cleanup path. It is plausible that it matters when a router hears a neighbor but does not receive evidence of a bidirectional link. It does not prove the defect caused a specific outage. Other aging and route cleanup paths, topology, interference, and coordinator behavior can also affect recovery. No original vendor source code was available.
