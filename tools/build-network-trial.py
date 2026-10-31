"""Build an experimental route-cost OTA from an already patched trial image."""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

PROFILES = {
    'plug': {'source':'59b68cdde3354d3284d8babd095545fba1dae2cc7c1b795dbcd116fd152eaa8b', 'result':'4df490316d07745c9727f5031876d6df79786b2bcedb63757b98550bf9f6b864', 'old':0x0102050a, 'new':0x0102050b, 'versions':(0x0e,0xd12,0x1db2b), 'label':0xd56, 'before':b'P1.05.10\0', 'after':b'P1.05.11\0', 'guard':0x17b50, 'block':0x17b58},
    'a60': {'source':'270a431b238fb5602bf7b03c2bafff45765808dc0c58c7313a0b889a100c625b', 'result':'50fd803b1140b3f3cd0539e20c6fa87085150a66bd9194077309d8e478414140', 'old':0x01020511, 'new':0x01020512, 'versions':(0x0e,0xdea,0x1e3c7), 'label':0xe56, 'before':b'P1.05.11\0', 'after':b'P1.05.12\0', 'guard':0x15778, 'block':0x15780},
}
BLOCK_BEFORE=bytes.fromhex('884234bf57181718a81d18218df8080019ea010f51d0')
BLOCK_AFTER=bytes.fromhex('884234bf5718171887f30807a81d029019f0180f51d0')


def crc(data):
    return (zlib.crc32(data,0xffffffff)^0xffffffff)&0xffffffff


def sections(data):
    offset, out = 56, []
    while offset < len(data):
        tag,size=struct.unpack_from('<HI',data,offset); start=offset+6; end=start+size
        if size<4 or end>len(data): raise ValueError('Invalid OTA subelement')
        p=data[start:end]
        if tag==0:
            if size<32: raise ValueError('Invalid main section')
            where,covered=start,p[8:12]+p[20:28]+p[32:]
        else: where,covered=end-4,p[:-4]
        out.append((tag,where,crc(covered)));offset=end
    if offset!=len(data) or [x[0] for x in out]!=[0,0xff01,0xff3e,0xff46]: raise ValueError('Unexpected layout')
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('model',choices=PROFILES);p.add_argument('source',type=Path);p.add_argument('--output-dir',type=Path,default=Path('build'))
    args=p.parse_args();spec=PROFILES[args.model];original=args.source.read_bytes()
    if hashlib.sha256(original).hexdigest()!=spec['source']:raise SystemExit('Unexpected source image')
    for _,where,value in sections(original):
        if struct.unpack_from('<I',original,where)[0]!=value:raise SystemExit('Source CRC mismatch')
    data=bytearray(original)
    for offset,before,after in ((spec['guard'],bytes.fromhex('08bf0920'),bytes.fromhex('19d000bf')),(spec['block'],BLOCK_BEFORE,BLOCK_AFTER)):
        if data[offset:offset+len(before)]!=before:raise SystemExit('Unexpected instructions')
        data[offset:offset+len(before)]=after
    for offset in spec['versions']:
        if struct.unpack_from('<I',data,offset)[0]!=spec['old']:raise SystemExit('Unexpected version')
        struct.pack_into('<I',data,offset,spec['new'])
    offset=spec['label']
    if data[offset:offset+9]!=spec['before']:raise SystemExit('Unexpected build label')
    data[offset:offset+9]=spec['after']
    for _,where,value in sections(data):struct.pack_into('<I',data,where,value)
    for _,where,value in sections(data):
        if struct.unpack_from('<I',data,where)[0]!=value:raise SystemExit('Output CRC mismatch')
    digest=hashlib.sha256(data).hexdigest()
    if digest!=spec['result']:raise SystemExit('Output differs from tested image')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    output=args.output_dir/(args.model+'-network-trial.ota');output.write_bytes(data)
    manifest={'source_sha256':spec['source'],'output_sha256':digest,'version':hex(spec['new']),'build_label':spec['after'].rstrip(b'\0').decode(),'status':'experimental; one device of this model booted'}
    (args.output_dir/(args.model+'-network-manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
