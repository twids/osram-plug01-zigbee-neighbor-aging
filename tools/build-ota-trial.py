"""Build the experimental Plug 01 neighbor-aging OTA locally. No network/device I/O."""
import argparse, hashlib, json, struct, zlib
from pathlib import Path

SOURCE_SHA256 = "c70126e43666f0a83077e8d93c587b7c0cefcd37d4719ebbeab1e33090b7c3b5"
OLD, NEW = 0x01020509, 0x0102050A
def crc(data): return (zlib.crc32(data, 0xFFFFFFFF) ^ 0xFFFFFFFF) & 0xFFFFFFFF

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path,help="Vendor Plug 01 OTA 0x01020509")
    p.add_argument("--output-dir",type=Path,default=Path("build"))
    a=p.parse_args(); original=a.source.read_bytes()
    digest=hashlib.sha256(original).hexdigest()
    if digest != SOURCE_SHA256 or len(original) != 121680: raise SystemExit("Unexpected vendor image hash or size")
    data=bytearray(original)
    if data[0xB88C:0xB890] != bytes.fromhex("01 f5 00 71") or data[0xB89E:0xB8A0] != bytes.fromhex("4b 29"): raise SystemExit("Unexpected code bytes; refusing to patch")
    data[0xB88C:0xB890]=bytes.fromhex("01 f1 80 01"); data[0xB89E:0xB8A0]=bytes.fromhex("13 29")
    for off in (0x0E,0xD12,0x1DB2B):
        if struct.unpack_from("<I",data,off)[0] != OLD: raise SystemExit(f"Unexpected version at {off:#x}")
        struct.pack_into("<I",data,off,NEW)
    if data[0xD56:0xD5F] != b"V1.05.09"+bytes([0]): raise SystemExit("Unexpected build label")
    data[0xD56:0xD5F]=b"P1.05.10"+bytes([0])
    off=56; checks=[]
    while off < len(data):
        tag,size=struct.unpack_from("<HI",data,off); start=off+6; end=start+size
        if end>len(data): raise SystemExit("Truncated OTA subelement")
        payload=data[start:end]
        if tag==0: value=crc(payload[8:12]+payload[20:28]+payload[32:]); pos=start
        else:
            if size<4: raise SystemExit("Invalid vendor subelement")
            value=crc(payload[:-4]); pos=end-4
        struct.pack_into("<I",data,pos,value); checks.append({"tag":hex(tag),"crc":hex(value)}); off=end
    if off != len(data) or len(checks)!=4: raise SystemExit("Unexpected OTA structure")
    a.output_dir.mkdir(parents=True,exist_ok=True); name="osram_plug01_P1.05.10_0x0102050a.ota"
    (a.output_dir/name).write_bytes(data)
    manifest={"source_sha256":digest,"output_sha256":hashlib.sha256(data).hexdigest(),"size":len(data),"version":hex(NEW),"build_label":"P1.05.10","changed_bytes":sum(x!=y for x,y in zip(original,data)),"checks":checks,"status":"experimental; one physical unit booted; broad RF benefit unproven"}
    (a.output_dir/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
