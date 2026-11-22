from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SHA256SUMS.txt"

files = sorted(
    path for path in ROOT.rglob("*")
    if path.is_file()
    and path != MANIFEST
    and ".git" not in path.parts
)

lines = [
    f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}"
    for path in files
]
MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {MANIFEST.name} for {len(files)} files.")
