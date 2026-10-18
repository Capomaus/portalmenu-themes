import argparse
import hashlib
import json
import os
import sys
import zipfile

ALLOWED = {"mp4", "ogg", "png", "jpg", "jpeg", "json"}

parser = argparse.ArgumentParser()
parser.add_argument("--base", default="https://raw.githubusercontent.com/Capomaus/portalmenu-themes/main")
args = parser.parse_args()

root = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(root, "themes")
entries = []
failed = False

for file in sorted(os.listdir(folder)):
    if not file.endswith(".zip"):
        continue
    theme_id = file[:-4]
    path = os.path.join(folder, file)
    with zipfile.ZipFile(path) as z:
        bad = [n for n in z.namelist() if not n.endswith("/") and n.rsplit(".", 1)[-1].lower() not in ALLOWED]
        unsafe = [n for n in z.namelist() if n.startswith("/") or ".." in n.split("/") or ":" in n]
    if bad or unsafe:
        print("rejected", file, bad + unsafe)
        failed = True
        continue
    meta_path = os.path.join(folder, theme_id + ".json")
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {}
    data = open(path, "rb").read()
    entry = {
        "id": theme_id,
        "name": meta.get("name", theme_id),
        "author": meta.get("author", ""),
        "description": meta.get("description", ""),
        "category": meta.get("category", ""),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "url": args.base + "/themes/" + file,
    }
    if os.path.exists(os.path.join(folder, theme_id + ".png")):
        entry["preview"] = args.base + "/themes/" + theme_id + ".png"
    entries.append(entry)

with open(os.path.join(root, "index.json"), "w", encoding="utf-8") as out:
    json.dump({"themes": entries}, out, indent=2)
    out.write("\n")

print(len(entries), "themes")
sys.exit(1 if failed else 0)
