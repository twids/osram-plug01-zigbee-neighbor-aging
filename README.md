# OSRAM Plug 01 Zigbee neighbor aging

Experimental firmware analysis of the OSRAM LIGHTIFY Plug 01 and Classic A60 W clear lamp. Both analyzed vendor images contain the same unreachable stale-neighbor cleanup branch; separate, model-specific trial images correct it.

**Status: experimental.** A modified image was installed and booted on one physical Plug 01 (OTA version 0x0102050a, Basic build label P1.05.10). The owner later reported improved stability after returning it to its original location, while Home Assistant history still showed multi-hour unavailable periods. This is encouraging, but does not prove the patch caused the improvement or is suitable for every unit.

One Classic A60 W clear bulb was also updated with a separately built image (OTA 0x01020511, Basic build P1.05.11). Transfer and a post-boot Zigbee attribute response were observed. Long-term behavior and practical network benefit remain unverified.

Both devices were subsequently updated with experimental route-cost and unknown-outgoing-link changes. A fresh post-boot read returned `P1.05.11` on the Plug 01 (OTA `0x0102050b`) and `P1.05.12` on the A60 (OTA `0x01020512`). These labels are model-specific; the same label may correspond to different OTA versions on different models. Long-term behavior remains unverified.

## Symptom and finding

One sibling-neighbor cleanup path increments a six-bit counter by four, masks it to 0–63, then compares it with 75. The removal branch cannot be reached. The candidate increments by one and compares against 19, preserving adjacent packed flags and a similar count-based delay.

The firmware also contains route discovery and route invalidation paths. This patch does not force a route to a particular device, guarantee a replacement route exists, or prove the defect caused any specific outage.

## Original firmware

The matching Plug 01 firmware 1.2.5.9 can be downloaded from [LEDVANCE's Zigbee firmware endpoint](https://api.update.ledvance.com/v1/zigbee/firmwares/download?Company=4364&Product=39&Version=1.2.5.9). The endpoint returns the OTA file directly. Expected size: 121,680 bytes. Expected SHA-256: c70126e43666f0a83077e8d93c587b7c0cefcd37d4719ebbeab1e33090b7c3b5. Verify it before building. The vendor binary is not mirrored here.

For the A60 W CLEAR, obtain version 1.2.5.16 (manufacturer 0x110c, image type 0x0013) from the [LEDVANCE firmware overview](https://update.ledvance.com/firmware-overview?sortOrder=manufacturer&submit=all). Expected size: 123,884 bytes; SHA-256: `173e9e77434118ebb5a0d83032063cf594cc201b42277a90e080b196497cf442`. Do not use the Plug 01 image or builder for the bulb.

## Contents

- [Patch analysis](docs/patch.md)
- [Build the experimental OTA locally](docs/build.md)
- [Home Assistant ZHA guide](docs/home-assistant.md)
- [Testing and limitations](docs/testing.md)
- [Additional network-code observations](docs/network-review.md)

## Scope and limitations

One physical unit of each model has been reported running its corresponding modified firmware. Long-term recovery, rollback, UART recovery, certification, and compatibility across variants are unknown. Installation is manual and intended for a single device. Do not enable network-wide automatic installation.

Not affiliated with OSRAM, LEDVANCE, Home Assistant, or the Connectivity Standards Alliance.
