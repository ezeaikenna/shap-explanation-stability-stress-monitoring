from pathlib import Path
import hashlib
import subprocess

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SHA256SUMS.txt"

result = subprocess.run(
    [
        "git", "ls-files", "-z",
        "--cached",
        "--others",
        "--exclude-standard",
    ],
    cwd=ROOT,
    check=True,
    capture_output=True,
)

paths = sorted({
    ROOT / entry.decode("utf-8")
    for entry in result.stdout.split(b"\0")
    if entry
})

files = [
    path for path in paths
    if path.is_file()
    and path.resolve() != MANIFEST.resolve()
]

lines = [
    f"{hashlib.sha256(path.read_bytes()).hexdigest()}  "
    f"{path.relative_to(ROOT).as_posix()}"
    for path in files
]

MANIFEST.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)

print(f"Wrote {MANIFEST.name} for {len(files)} Git-visible files.")
