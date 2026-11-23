"""Generate SHA-256 checksums for the exact Git index snapshot.

Only files present in the Git index are included. Each file's bytes are read
from the index with ``git show :path``, never from the working tree. Therefore,
unstaged working-tree edits cannot contaminate the manifest.

After running this script, stage the regenerated SHA256SUMS.txt before
committing. The manifest itself is excluded from its own checksum list.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST_NAME = "SHA256SUMS.txt"


def git_index_paths(root: Path) -> list[str]:
    """Return paths tracked in the current Git index, including staged adds."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached"],
        check=True,
        capture_output=True,
    )
    return sorted(
        path.decode("utf-8", errors="surrogateescape")
        for path in result.stdout.split(b"\0")
        if path
    )


def git_index_blob(root: Path, path: str) -> bytes:
    """Read a file's staged/index blob, not its working-tree contents."""
    result = subprocess.run(
        ["git", "-C", str(root), "show", f":{path}"],
        check=True,
        capture_output=True,
    )
    return result.stdout


def generate_manifest(root: Path = ROOT) -> list[str]:
    """Write SHA256SUMS.txt from the Git index and return its manifest lines."""
    root = root.resolve()
    check = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    if check.returncode != 0 or check.stdout.strip() != "true":
        raise RuntimeError(f"Not a Git worktree: {root}")

    entries: list[str] = []
    for relative_path in git_index_paths(root):
        if relative_path == MANIFEST_NAME:
            continue
        blob = git_index_blob(root, relative_path)
        digest = hashlib.sha256(blob).hexdigest()
        entries.append(f"{digest}  {relative_path}")

    manifest = root / MANIFEST_NAME
    manifest.write_text(
        "\n".join(entries) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return entries


def main() -> int:
    try:
        entries = generate_manifest()
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"ERROR: could not generate index-based manifest: {exc}", file=sys.stderr)
        return 2
    print(
        f"Wrote {MANIFEST_NAME} for {len(entries)} files from the Git index "
        "(unstaged working-tree changes excluded)."
    )
    print(f"Next: stage {MANIFEST_NAME} and verify the staged snapshot before committing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
