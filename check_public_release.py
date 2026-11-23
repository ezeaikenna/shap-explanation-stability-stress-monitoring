#!/usr/bin/env python3
"""Pre-release privacy scan for the SHAP research repository.

Checks known restricted paths, suspicious structured-data headers/keys, staged
Git blobs, and (optionally) paths and structured-data blobs in reachable Git
history. This is a conservative safeguard, not a privacy certification.
"""
from __future__ import annotations
import argparse, csv, io, json, re, subprocess, sys
from pathlib import Path

BLOCKED_FILENAMES = {
    "RELAX_next_morning_stress_dataset.csv", "RELAX_local_SHAP_observation_stability_pseudonymised.csv",
    "RELAX_local_SHAP_participant_stability_pseudonymised.csv", "RELAX_local_SHAP_values.npy",
    "RELAX_local_SHAP_fold_allocation_summary.csv", "RELAX_local_SHAP_run_metadata.json",
    "RELAX_global_SHAP_heldout_values.csv", "RELAX_global_SHAP_fold_audit.csv",
    "RELAX_global_SHAP_integrity_checks.csv",
    "SSAQS_prediction_comparison.csv", "SSAQS_global_SHAP_heldout_values.csv",
    "SSAQS_global_SHAP_oof_predictions.csv", "SSAQS_Global_SHAP_outputs.zip",
}
BLOCKED_DIRECTORY_NAMES = {"SSAQS_Global_SHAP_Analysis", "RELAX_Global_SHAP_Controlled_Notebook_Run"}
DATA_SUFFIXES = {".csv", ".tsv", ".json", ".jsonl"}
SENSITIVE_FIELDS = re.compile(r"(^|[^a-z])(participant[_ -]?(id|code|key)|subject[_ -]?(id|code)|user[_ -]?id|record[_ -]?id|timestamp|datetime|event[_ -]?time|row[_ -]?index|individual[_ -]?id)([^a-z]|$)", re.I)
SENSITIVE_NORMALIZED_FIELDS = {
    "participantid", "participantcode", "participantkey",
    "subjectid", "subjectcode", "userid", "recordid",
    "timestamp", "datetime", "eventtime", "rowindex", "individualid",
}


def is_sensitive_field(field: str) -> bool:
    """Match common sensitive field names across snake_case and camelCase."""
    normalized = re.sub(r"[^a-z0-9]", "", field.lower())
    return bool(SENSITIVE_FIELDS.search(field)) or normalized in SENSITIVE_NORMALIZED_FIELDS


def is_blocked_path(path_text: str) -> str | None:
    normalized = path_text.replace("\\", "/").strip("/")
    parts = [p for p in normalized.split("/") if p and p != "."]
    if not parts: return None
    for part in parts:
        if part in BLOCKED_DIRECTORY_NAMES: return f"local-only workspace: {normalized}"
    if parts[-1] in BLOCKED_FILENAMES: return f"restricted generated file: {normalized}"
    if "RELAX_Participant_Level" in parts and "outputs" in parts: return f"participant-level output directory/file: {normalized}"
    return None


def inspect_structured_content(path_text: str, data: bytes) -> str | None:
    suffix = Path(path_text).suffix.lower()
    if suffix not in DATA_SUFFIXES: return None
    try: text = data.decode("utf-8-sig")
    except UnicodeDecodeError: return "invalid UTF-8 encoding"
    fields: list[str] = []
    try:
        if suffix in {".csv", ".tsv"}:
            first = next(csv.reader(io.StringIO(text), delimiter="\t" if suffix == ".tsv" else ","), [])
            fields = [str(x) for x in first]
        else:
            def walk(x):
                if isinstance(x, dict):
                    fields.extend(map(str, x.keys()))
                    for v in x.values():
                        walk(v)
                elif isinstance(x, list):
                    for v in x:
                        walk(v)

            if suffix == ".jsonl":
                # JSON Lines contains one independent JSON value per nonblank line.
                # Fail closed on malformed records rather than silently skipping them.
                for line_number, line in enumerate(text.splitlines(), start=1):
                    if not line.strip():
                        continue
                    try:
                        walk(json.loads(line))
                    except json.JSONDecodeError:
                        return f"invalid JSONL record at line {line_number}"
            else:
                walk(json.loads(text))
    except json.JSONDecodeError:
        return "invalid JSON document"
    hits = sorted({f for f in fields if is_sensitive_field(f)})
    return "sensitive-looking structured field(s): " + ", ".join(hits) if hits else None


def scan_worktree(root: Path) -> list[str]:
    findings=[]
    for p in root.rglob("*"):
        rel=p.relative_to(root)
        if ".git" in rel.parts: continue
        reason=is_blocked_path(rel.as_posix())
        if reason: findings.append(reason)
        elif p.is_file() and p.suffix.lower() in DATA_SUFFIXES:
            try:
                content_reason = inspect_structured_content(rel.as_posix(), p.read_bytes())
            except OSError as exc:
                content_reason = f"could not read structured file ({exc.__class__.__name__})"
            if content_reason:
                findings.append(f"{rel.as_posix()}: {content_reason}")
    return sorted(set(findings))


def git_root(root: Path) -> bool:
    p=subprocess.run(["git","-C",str(root),"rev-parse","--is-inside-work-tree"],capture_output=True,text=True)
    return p.returncode == 0 and p.stdout.strip() == "true"


def staged_findings(root: Path) -> tuple[list[str], str | None]:
    if not git_root(root): return [], "Not a Git worktree; staged scan skipped."
    p=subprocess.run(["git","-C",str(root),"diff","--cached","--name-only","--diff-filter=ACMR","-z"],capture_output=True)
    if p.returncode: return [], "Git could not read staged index."
    found=[]
    for raw in p.stdout.split(b"\0"):
        if not raw: continue
        path=raw.decode("utf-8", "replace")
        reason=is_blocked_path(path)
        if reason: found.append("staged " + reason); continue
        blob=subprocess.run(["git","-C",str(root),"show",f":{path}"],capture_output=True)
        if blob.returncode != 0:
            found.append(f"staged {path}: could not read staged Git blob")
            continue
        content_reason=inspect_structured_content(path, blob.stdout)
        if content_reason: found.append(f"staged {path}: {content_reason}")
    return found, None


def history_findings(root: Path) -> tuple[list[str], str | None]:
    """Inspect every reachable commit tree path and each structured blob.

    Tree paths are enumerated per commit, independently of blob deduplication,
    so the same blob stored under ordinary and restricted paths cannot hide
    the restricted path. Only commits reachable from local refs are covered.
    """
    if not git_root(root): return [], "Not a Git worktree; history scan skipped."
    commits = subprocess.run(
        ["git", "-C", str(root), "rev-list", "--all"],
        capture_output=True, text=True,
    )
    if commits.returncode:
        return [], "Git history commit scan failed."
    found = []
    scanned_blobs = set()
    for commit in commits.stdout.splitlines():
        tree = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "-z", "--full-tree", commit],
            capture_output=True,
        )
        if tree.returncode:
            found.append(f"historical commit {commit[:12]}: could not enumerate tree")
            continue
        for entry in tree.stdout.split(b"\0"):
            if not entry:
                continue
            try:
                metadata, raw_path = entry.split(b"\t", 1)
                mode, kind, oid = metadata.decode("ascii").split()
                path = raw_path.decode("utf-8", "surrogateescape")
            except (ValueError, UnicodeDecodeError):
                found.append(f"historical commit {commit[:12]}: unparseable tree entry")
                continue
            reason = is_blocked_path(path)
            if reason:
                found.append("historical " + reason)
            suffix = Path(path).suffix.lower()
            if kind != "blob" or suffix not in DATA_SUFFIXES:
                continue
            key = (oid, suffix)
            if key in scanned_blobs:
                continue
            scanned_blobs.add(key)
            blob = subprocess.run(
                ["git", "-C", str(root), "cat-file", "blob", oid],
                capture_output=True,
            )
            if blob.returncode:
                found.append(f"historical {path}: could not read Git blob")
                continue
            content_reason = inspect_structured_content(path, blob.stdout)
            if content_reason:
                found.append(f"historical {path}: {content_reason}")
    return sorted(set(found)), None


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument("--require-git",action="store_true")
    ap.add_argument("--history",action="store_true",help="also scan paths in reachable local Git history")
    a=ap.parse_args(); root=a.root.expanduser().resolve()
    if not root.is_dir(): print(f"ERROR: missing root: {root}",file=sys.stderr); return 2
    findings=scan_worktree(root)
    staged,note=staged_findings(root)
    if note and a.require_git: print("FAIL: "+note); return 2
    findings += staged
    if a.history:
        hist,hnote=history_findings(root)
        if hnote and a.require_git: print("FAIL: "+hnote); return 2
        findings += hist
        if hnote: print("NOTE: "+hnote)
    if note: print("NOTE: "+note)
    if findings:
        print("FAIL: potential restricted content detected:")
        for f in sorted(set(findings)): print(" - "+f)
        return 1
    print("PASS: no known restricted paths or sensitive-looking structured fields detected.")
    print("NOTE: history scan is opt-in (--history) and inspects reachable local Git refs for blocked paths and CSV/TSV/JSON/JSONL blob fields.")
    print("NOTE: fetch remote branches first; unreachable objects, unfetched refs, other binary formats and semantic disclosure risk are not covered.")
    print("NOTE: this tool cannot establish anonymity, inspect every binary format, or replace manual privacy and disclosure review.")
    return 0

if __name__ == "__main__": raise SystemExit(main())
