# Build the experimental OTA locally

The repository does not include the vendor firmware or the generated OTA image. Download the vendor file from the LEDVANCE endpoint linked in the README, verify its SHA-256, then run the standard-library-only builder from the repository root:

    python tools/build-ota-trial.py path/to/vendor-plug01-0x01020509.ota

The script verifies the source digest and expected instruction bytes, patches only the documented cleanup instructions, increments the OTA version to 0x0102050a, sets the Basic build label to P1.05.10, and recalculates the OTA integrity fields. It writes the image and a manifest under build/. Review both before using the image.

The output is a modified vendor firmware image. Keep it local; do not upload the generated OTA to this repository. This build recipe is experimental and should be reproduced and independently checked before deployment.

For the **Classic A60 W clear**, use its own vendor image and its separate builder:

    python tools/build-a60-ota-trial.py path/to/vendor-a60-0x01020510.ota

The A60 builder verifies the source identity, SHA-256, expected instructions and four stored integrity fields. It changes the two cleanup instructions, the three version fields, and build label, recalculates the integrity fields, and requires the output SHA-256 `270a431b238fb5602bf7b03c2bafff45765808dc0c58c7313a0b889a100c625b`. The output is `0x01020511`, label `P1.05.11`. It is experimental; physical rollback and compatibility with other variants are not established.

For the later experimental network corrections, first build the matching neighbor-aging image above, then use it as the input to the separate network builder:

    python tools/build-network-trial.py plug path/to/osram_plug01_P1.05.10_0x0102050a.ota
    python tools/build-network-trial.py a60 path/to/osram_a60_P1.05.11_01020511.ota

Each invocation checks the exact source hash and instruction bytes, applies its model-specific offsets, updates versions and build label, checks all OTA CRCs, and verifies the output hash. Output versions are Plug `0x0102050b` / `P1.05.11` and A60 `0x01020512` / `P1.05.12`. See [network review](network-review.md) for tested behavior and important limitations.
