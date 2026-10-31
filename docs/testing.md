## Testing and evidence

The unreachable compare was verified against vendor instruction bytes, range analysis, independent disassembly, and Thumb emulation. Emulator cases checked the six-bit counter, surrounding flags, qualifying and nonqualifying sibling records, and how the cleanup state responds to missing and restored bidirectional observations. These are code-path tests, not RF tests.

One modified OTA image was installed on one physical OSRAM Plug 01. Home Assistant reported version 0x0102050a; a fresh Basic cluster sw_build_id read returned P1.05.10. This confirms transfer, application boot, and a Zigbee attribute response from that unit. The owner subsequently reported better stability at the original location, though HA history still recorded multi-hour unavailable intervals.

This is a single-device experiment. It does not establish that the defect caused the original dropouts, that the patch improves all networks, or that rollback/UART recovery is available. Hardware variants and certification are not verified.

On the Classic A60 W clear image, the corresponding 56-byte original function matched the plug's original routine. The final bulb candidate's Thumb code was executed in Unicorn with 640 relation/precondition/flag combinations and all 64 initial counter values. From zero, it reached the removal destination on the 19th qualifying call; the original never reached it in 1,024 calls. The destination was intercepted: this was not a whole-stack or RF test. All four integrity fields were cross-checked with two CRC implementations and Zigpy 2.3.0 parsed and round-tripped the final image with positive and negative model, image-type and version matching checks.

One physical A60 bulb completed transfer; Home Assistant subsequently reported `0x01020511`, and a fresh Basic `sw_build_id` read returned `P1.05.11`. The HTTP request returned 502 while transfer continued, so the claim rests on the observed progress, post-install version and fresh build read. Long-term behavior, rollback and network benefit are not established.

The later network-correction images completed transfer on the same two devices. Fresh Basic reads returned Plug `P1.05.11` and A60 `P1.05.12`, with HA OTA versions `0x0102050b` and `0x01020512`. The long-running HTTP requests returned 502 while transfers continued; observed progress, reported versions and fresh reads provide the installation evidence. See [network review](network-review.md) for emulator coverage and limits.
