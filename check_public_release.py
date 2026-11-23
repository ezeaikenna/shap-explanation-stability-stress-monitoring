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
    except UnicodeDecodeError: return None
    fields: list[str] = []
    try:
        if suffix in {".csv", ".tsv"}:
            first = next(csv.reader(io.StringIO(text), delimiter="\t" if suffix == ".tsv" else ","), [])
            fields = [str(x) for x in first]
        else:
            obj = json.loads(text)
            def walk(x):
                if isinstance(x, dict):
                    fields.extend(map(str, x.keys()))
                    for v in x.values(): walk(v)
                elif isinstance(x, list):
                    for v in x: walk(v)
            walk(obj)
    except Exception: return None
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
            try: content_reason=inspect_structured_content(rel.as_posix(), p.read_bytes())
            except OSError: content_reason=None
            if content_reason: findings.append(f"{rel.as_posix()}: {content_reason}")
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
        if blob.returncode == 0:
            content_reason=inspect_structured_content(path, blob.stdout)
            if content_reason: found.append(f"staged {path}: {content_reason}")
    return found, None


def history_findings(root: Path) -> tuple[list[str], str | None]:
    """Inspect reachable local Git history for blocked paths and structured blobs.

    Uses `git rev-list --objects --all`, so only objects reachable from refs
    present in this local clone are covered. Fetch remote branches first when
    they must be included. Binary formats and semantic disclosure are out of scope.
    """
    if not git_root(root): return [], "Not a Git worktree; history scan skipped."
    p=subprocess.run(["git","-C",str(root),"rev-list","--objects","--all"],capture_output=True,text=True)
    if p.returncode: return [], "Git history object scan failed."
    found=[]
    seen=set()
    for line in p.stdout.splitlines():
        if not line.strip(): continue
        pieces=line.split(" ",1)
        oid=pieces[0]
        path=pieces[1] if len(pieces)>1 else ""
        if path:
            reason=is_blocked_path(path)
            if reason: found.append("historical " + reason)
        if not path or oid in seen or Path(path).suffix.lower() not in DATA_SUFFIXES:
            continue
        seen.add(oid)
        kind=subprocess.run(["git","-C",str(root),"cat-file","-t",oid],capture_output=True,text=True)
        if kind.returncode or kind.stdout.strip() != "blob": continue
        blob=subprocess.run(["git","-C",str(root),"cat-file","blob",oid],capture_output=True)
        if blob.returncode: continue
        content_reason=inspect_structured_content(path,blob.stdout)
        if content_reason: found.append(f"historical {path}: {content_reason}")
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
    print("NOTE: history scan is opt-in (--history) and inspects reachable local Git refs for blocked paths and CSV/TSV/JSON blob fields.")
    print("NOTE: fetch remote branches first; unreachable objects, unfetched refs, other binary formats and semantic disclosure risk are not covered.")
    print("NOTE: this tool cannot establish anonymity, inspect every binary format, or replace human/institutional review.")
    return 0

if __name__ == "__main__": raise SystemExit(main())
