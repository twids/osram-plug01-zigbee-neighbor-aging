# Additional network-code observations

The following are separate from the patched six-bit cleanup defect. They were inspected in the original Plug 01 (`0x01020509`) and A60 W clear (`0x01020510`) images. The corresponding instruction fragments are unchanged in the two installed trial images. Neither observation has been patched or shown to cause a real-world outage.

## Path-cost truncation at high values

The route-request cost fragment loads an existing path-cost byte and adds the larger of two neighbor link costs. Later it truncates the sum to eight bits before comparing it with an existing discovery-table cost. Relevant app addresses are `0x117ae6–0x117b00` and `0x117be4–0x117bea` on the plug, and `0x11570e–0x115728` and `0x11580c–0x115812` on the bulb.

In isolated execution of the actual Thumb fragments, a previous cost of 250 and link costs of 7 yield the 32-bit sum 257; truncation changes it to 1, so it takes the lower-cost branch against an existing cost of 10. A sum of 256 similarly becomes zero. This is a reproducible arithmetic edge case, not proof that such a high path cost can reach the comparison through the full receive path in a normal network. Hop limits, upstream validation and complete packet processing were not simulated; no packet was sent and no routing change was made. The likelihood and practical effect are unknown.

## Unknown link cost

The same fragment substitutes 9 when either directional cost is zero and uses the maximum. For example, `(incoming=1, outgoing=0)` contributes 9. The [2023 Zigbee specification](https://csa-iot.org/wp-content/uploads/2023/04/05-3474-23-csg-zigbee-specification-compressed.pdf) describes rejecting a route request when the outgoing cost is unknown, and [Silicon Labs' explanation](https://docs.silabs.com/zigbee/latest/zigbee-fundamentals/04-zigbee-routing-concepts) describes the same approach. These are modern comparison references, not proof of a certification violation in these older devices. An earlier check may exclude zero outgoing cost before the fragment; the complete receive path has not been established, so this remains a suspicion rather than a confirmed functional bug.

## Reproduce the fragment experiment

Install Unicorn 2.1.4 in an isolated Python environment and supply the respective vendor images with the SHA-256 values in the README:

```sh
python tools/probe-route-cost.py plug /path/to/plug-vendor.ota
python tools/probe-route-cost.py a60 /path/to/a60-vendor.ota
```

The script checks the source hash and instruction bytes, runs the addition and comparison fragments with explicit synthetic inputs, and checks the observed branch. It does not execute the intervening handler, prove inputs reachable or simulate radio traffic.
