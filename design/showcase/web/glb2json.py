"""Konversi .glb -> glTF JSON dengan buffer base64 tertanam (disajikan sebagai .json di artifact)."""
import base64, json, struct, sys
for src in sys.argv[1:]:
    b = open(src, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    off = 20 + n
    blen = struct.unpack("<I", b[off:off + 4])[0]
    binc = b[off + 8:off + 8 + blen]
    j["buffers"][0]["uri"] = "data:application/octet-stream;base64," + base64.b64encode(binc).decode()
    out = src[:-4] + ".json"
    open(out, "w").write(json.dumps(j, separators=(",", ":")))
    print(out, len(open(out).read()) // 1024, "KB")
