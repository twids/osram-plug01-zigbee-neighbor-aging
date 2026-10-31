"""Build the experimental Classic A60 W clear OTA locally; no network or device I/O."""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

SOURCE_SHA256 = '173e9e77434118ebb5a0d83032063cf594cc201b42277a90e080b196497cf442'
OUTPUT_SHA256 = '270a431b238fb5602bf7b03c2bafff45765808dc0c58c7313a0b889a100c625b'
OLD, NEW = 0x01020510, 0x01020511


def crc(data):
    return (zlib.crc32(data, 0xffffffff) ^ 0xffffffff) & 0xffffffff


def inspect_sections(data):
    offset, sections = 56, []
    while offset < len(data):
        tag, size = struct.unpack_from('<HI', data, offset)
        start, end = offset + 6, offset + 6 + size
        if size < 4 or end > len(data):
            raise ValueError('Invalid OTA subelement')
        payload = data[start:end]
        if tag == 0:
            if size < 32: raise ValueError('Invalid main subelement')
            position, covered = start, payload[8:12] + payload[20:28] + payload[32:]
        else:
            position, covered = end - 4, payload[:-4]
        sections.append((tag, position, crc(covered)))
        offset = end
    if offset != len(data) or [x[0] for x in sections] != [0, 0xff01, 0xff3e, 0xff46]:
        raise ValueError('Unexpected OTA layout')
    return sections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Vendor A60 W CLEAR OTA 0x01020510')
    parser.add_argument('--output-dir', type=Path, default=Path('build'))
    args = parser.parse_args()
    original = args.source.read_bytes()
    if len(original) != 123884 or hashlib.sha256(original).hexdigest() != SOURCE_SHA256:
        raise SystemExit('Unexpected vendor image hash or size')
    if struct.unpack_from('<IHHHHHI', original) != (0x0beef11e, 0x0100, 56, 0, 0x110c, 0x0013, OLD):
        raise SystemExit('Unexpected OTA identity')
    for _, position, value in inspect_sections(original):
        if struct.unpack_from('<I', original, position)[0] != value:
            raise SystemExit('Original integrity check failed')
    data = bytearray(original)
    for offset, before, after in [(0xbef0, '01f50071', '01f18001'), (0xbf02, '4b29', '1329')]:
        before, after = bytes.fromhex(before), bytes.fromhex(after)
        if data[offset:offset+len(before)] != before: raise SystemExit('Unexpected instruction bytes')
        data[offset:offset+len(before)] = after
    for offset in (0x0e, 0x0dea, 0x1e3c7):
        if struct.unpack_from('<I', data, offset)[0] != OLD: raise SystemExit('Unexpected version field')
        struct.pack_into('<I', data, offset, NEW)
    if data[0xe56:0xe5f] != b'V1.05.10\0': raise SystemExit('Unexpected build label')
    data[0xe56:0xe5f] = b'P1.05.11\0'
    for _, position, value in inspect_sections(data):
        struct.pack_into('<I', data, position, value)
    for _, position, value in inspect_sections(data):
        if struct.unpack_from('<I', data, position)[0] != value: raise SystemExit('Output integrity failed')
    digest = hashlib.sha256(data).hexdigest()
    if digest != OUTPUT_SHA256: raise SystemExit('Output differs from the verified trial')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / 'osram_a60_P1.05.11_01020511.ota'
    output.write_bytes(data)
    manifest = {'source_sha256': SOURCE_SHA256, 'output_sha256': digest, 'version': hex(NEW),
                'build_label': 'P1.05.11', 'size': len(data), 'status': 'experimental; one bulb booted'}
    (args.output_dir / 'a60-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
