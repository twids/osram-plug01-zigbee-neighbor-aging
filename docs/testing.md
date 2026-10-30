## Testing and evidence

The unreachable compare was verified against vendor instruction bytes, range analysis, independent disassembly, and Thumb emulation. Emulator cases checked the six-bit counter, surrounding flags, qualifying and nonqualifying sibling records, and how the cleanup state responds to missing and restored bidirectional observations. These are code-path tests, not RF tests.

One modified OTA image was installed on one physical OSRAM Plug 01. Home Assistant reported version 0x0102050a; a fresh Basic cluster sw_build_id read returned P1.05.10. This confirms transfer, application boot, and a Zigbee attribute response from that unit. The owner subsequently reported better stability at the original location, though HA history still recorded multi-hour unavailable intervals.

This is a single-device experiment. It does not establish that the defect caused the original dropouts, that the patch improves all networks, or that rollback/UART recovery is available. Hardware variants and certification are not verified.
