"""Execute isolated route-cost fragments from both vendor OTA images, offline.

Requires unicorn 2.1.4. This is not a packet or full-stack test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import unicorn
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R5, UC_ARM_REG_R7, UC_ARM_REG_R10

IMAGES = {
    'plug': ('c70126e43666f0a83077e8d93c587b7c0cefcd37d4719ebbeab1e33090b7c3b5', 0x1d73a, 0x117ae6, 0x117be4, 0x117d08),
    'a60': ('173e9e77434118ebb5a0d83032063cf594cc201b42277a90e080b196497cf442', 0x1dfd6, 0x11570e, 0x11580c, 0x115930),
}


def run(model, source):
    expected, end, calc, compare, reject = IMAGES[model]
    ota = source.read_bytes()
    if hashlib.sha256(ota).hexdigest() != expected: raise SystemExit('Unexpected vendor image')
    code = ota[0x5e:end]
    assert code[calc-0x100000:calc-0x100000+4] == bytes.fromhex('807c10f0')
    assert code[compare-0x100000:compare-0x100000+6] == bytes.fromhex('6879ffb28742')
    cpu = unicorn.Uc(unicorn.UC_ARCH_ARM, unicorn.UC_MODE_THUMB | unicorn.UC_MODE_MCLASS)
    cpu.mem_map(0x100000, 0x30000); cpu.mem_write(0x100000, code); cpu.mem_map(0x200000, 0x2000)
    results = []
    for previous, incoming, outgoing, existing in [(10,1,1,20), (10,1,1,5), (0,1,0,20), (250,7,7,10), (249,7,7,10), (250,0,1,10)]:
        cpu.mem_write(0x200012, bytes([incoming | outgoing << 4]))
        cpu.mem_write(0x200105, bytes([previous])); cpu.mem_write(0x200205, bytes([existing]))
        cpu.reg_write(UC_ARM_REG_R0, 0x200000); cpu.reg_write(UC_ARM_REG_R10, 0x200100); cpu.reg_write(UC_ARM_REG_R5, 0x200200)
        cpu.emu_start(calc | 1, calc + 0x1c, count=20)
        total = cpu.reg_read(UC_ARM_REG_R7); reached = []
        def stop(uc, address, size, context):
            reached.append(address); uc.emu_stop()
        h1 = cpu.hook_add(unicorn.UC_HOOK_CODE, stop, begin=compare+10, end=compare+10)
        h2 = cpu.hook_add(unicorn.UC_HOOK_CODE, stop, begin=reject, end=reject)
        cpu.emu_start(compare | 1, 0, count=10)
        cpu.hook_del(h1); cpu.hook_del(h2)
        assert len(reached) == 1 and total == previous + max(incoming or 9, outgoing or 9)
        compared = cpu.reg_read(UC_ARM_REG_R7)
        assert compared == total & 0xff and (reached[0] == reject) == (compared >= existing)
        results.append({'previous': previous, 'incoming': incoming, 'outgoing': outgoing,
                        'existing_cost': existing, 'sum': total, 'compared': compared,
                        'branch': 'reject' if reached[0] == reject else 'lower-cost path'})
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('model', choices=IMAGES)
    p.add_argument('vendor_ota', type=Path)
    args = p.parse_args()
    print(json.dumps({'model': args.model, 'results': run(args.model, args.vendor_ota),
                      'limits': 'isolated fragments; input reachability and actual routing not tested'}, indent=2))


if __name__ == '__main__': main()
