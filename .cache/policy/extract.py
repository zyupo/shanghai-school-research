#!/usr/bin/env python3
import zipfile, re, sys, os

files = [
    ("qa-2026.docx", "qa-2026.txt"),
    ("zhaosheng-tonggao.docx", "zhaosheng-tonggao.txt"),
]
base = os.path.dirname(os.path.abspath(__file__))
for src, dst in files:
    sp = os.path.join(base, src)
    dp = os.path.join(base, dst)
    try:
        with zipfile.ZipFile(sp) as z:
            with z.open("word/document.xml") as f:
                xml = f.read().decode("utf-8", errors="ignore")
        # Replace paragraph/line breaks and tables with newlines
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
        xml = re.sub(r"</w:tr>", "\n", xml)
        xml = re.sub(r"</w:tc>", "\t", xml)
        # Strip all other tags
        text = re.sub(r"<[^>]+>", "", xml)
        text = re.sub(r"\n{2,}", "\n\n", text)
        with open(dp, "w", encoding="utf-8") as out:
            out.write(text)
        print(f"ok: {src} -> {dst} ({len(text)} chars)")
    except Exception as e:
        print(f"err: {src}: {e}", file=sys.stderr)

# Handle .doc (old binary format): try catdoc fallback, else skip
src = "renhu-fenli.doc"
sp = os.path.join(base, src)
try:
    with open(sp, "rb") as f:
        data = f.read(8)
    print(f"renhu-fenli.doc first bytes: {data}")
    # Old .doc is OLE2 - try strings-like extraction
    with open(sp, "rb") as f:
        raw = f.read()
    # extract Chinese text (UTF-16 LE, which Word commonly uses)
    try:
        txt = raw.decode("utf-16-le", errors="ignore")
    except Exception:
        txt = raw.decode("gbk", errors="ignore")
    # filter printable Chinese + punctuation
    text = re.sub(r"[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef0-9A-Za-z，。、；：！？“”‘’（）《》——\-·年月日 　\n\r\t]", "", txt)
    text = re.sub(r"\s+", " ", text)
    with open(os.path.join(base, "renhu-fenli.txt"), "w", encoding="utf-8") as out:
        out.write(text)
    print(f"ok-raw: {src} ({len(text)} chars)")
except Exception as e:
    print(f"err: {src}: {e}", file=sys.stderr)
