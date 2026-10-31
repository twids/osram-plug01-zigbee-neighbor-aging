# Home Assistant ZHA OTA guide

This is an experimental manual process for one OSRAM Plug 01. Failed boot recovery, UART recovery, and downgrade have not been established. Back up Home Assistant and understand the risk before proceeding.

1. Obtain the matching vendor OTA image from the LEDVANCE link in the repository README. Verify its SHA-256.
2. Build the modified image locally using build.md; review the output manifest and hash. Do not distribute the vendor image.
3. Add the generated image to a local Zigpy OTA provider used by ZHA. Merge it under the existing zha -> zigpy_config -> ota configuration; do not add a duplicate top-level zha key. Configuration varies by release.
4. Keep automatic OTA disabled. Provider matching may apply to all devices with the same model and current firmware; it may not be scoped to one IEEE address.
5. Confirm the offered image is for the intended Plug 01. Start the update manually for that device only and do not interrupt power during transfer.
6. Confirm HA reports version 0x0102050a, then read Basic cluster sw_build_id on endpoint 3 and confirm P1.05.10. Observe normal operation.
7. Remove the experimental provider and image if you do not intend to keep the test firmware. Do not assume the original image can downgrade the plug.

Consult current Home Assistant, ZHA, and Zigpy documentation for configuration details matching your installed versions. This is not a tested recovery procedure.

For the Classic A60 W clear, the same principles apply, but use **only** its separate builder and image. The tested transition was `0x01020510` to `0x01020511`; the fresh endpoint 3 Basic `sw_build_id` read was `P1.05.11`. Provider matching by model and version is not per-IEEE: install manually on the intended device only and remove the temporary offer afterward. Do not use the Plug 01 OTA for a bulb.
