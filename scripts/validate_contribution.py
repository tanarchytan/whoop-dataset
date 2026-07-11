#!/usr/bin/env python3
"""Validate WHOOP dataset contributions.

Enforces the repo's safety + structure rules so sensitive or malformed data can't land:

  * no journal_entries.csv (or any "journal" file) - the one export file that can hold sensitive data
  * only the allowed files (the three metric CSVs + metadata.yml + optional NOTES/README)
  * no email address (or other obvious PII) anywhere in the contributed text
  * a complete metadata.yml with the required confirmations set to true
  * a pseudonymous folder name (never a real name)

Standard library only - no `pip install`. Run:

    python3 scripts/validate_contribution.py                     # all contributions
    python3 scripts/validate_contribution.py contributions/user-3f9a   # one folder
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRIB = ROOT / "contributions"

ALLOWED_DEVICES = {"3.0", "4.0", "5.0", "MG"}
METRIC_CSVS = {"physiological_cycles.csv", "sleeps.csv", "workouts.csv"}
ALLOWED_FILES = METRIC_CSVS | {"metadata.yml", "notes.md", "readme.md"}
REQUIRED_KEYS = ["pseudonym", "devices", "date_range", "files"]
REQUIRED_TRUE = ["anonymized", "journal_excluded", "consent_public"]

FOLDER_RE = re.compile(r"^user[-_]?[a-z0-9]+$", re.IGNORECASE)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TEXT_SUFFIXES = {".csv", ".yml", ".yaml", ".md", ".txt", ".json"}


def _scalar(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        return v[1:-1]
    low = v.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    return v


def parse_metadata(text: str) -> dict:
    """Tiny YAML-subset parser for our flat metadata (one level of nesting for lists/date_range)."""
    data: dict = {}
    cur_key = None
    cur_mode = None  # 'list' | 'map' | None
    for raw in text.splitlines():
        if raw.lstrip().startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", raw).rstrip()  # strip inline comments
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        s = line.strip()
        if indent == 0:
            cur_key, cur_mode = None, None
            if s.endswith(":"):
                cur_key = s[:-1].strip()
                data[cur_key] = None
            else:
                k, _, val = s.partition(":")
                data[k.strip()] = _scalar(val)
        elif cur_key is not None:
            if s.startswith("- "):
                if cur_mode is None:
                    data[cur_key], cur_mode = [], "list"
                data[cur_key].append(_scalar(s[2:]))
            else:
                if cur_mode is None:
                    data[cur_key], cur_mode = {}, "map"
                k, _, val = s.partition(":")
                data[cur_key][k.strip()] = _scalar(val)
    return data


def validate_folder(folder: Path) -> list[str]:
    errs: list[str] = []
    name = folder.name

    if not FOLDER_RE.match(name):
        errs.append(f"folder name '{name}' must be a pseudonym like 'user-3f9a' (never a real name)")

    # --- file allow-list + journal ban ---
    present_csvs = set()
    for f in sorted(folder.rglob("*")):
        if f.is_dir():
            continue
        rel = f.relative_to(folder).as_posix()
        low = f.name.lower()
        if "journal" in low:
            errs.append(f"{rel}: journal files are forbidden - remove it (may contain sensitive data)")
            continue
        if low not in ALLOWED_FILES:
            errs.append(f"{rel}: not an allowed file (only the 3 metric CSVs + metadata.yml + NOTES/README)")
            continue
        if low in METRIC_CSVS:
            present_csvs.add(low)
        # --- PII scan ---
        if f.suffix.lower() in TEXT_SUFFIXES:
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                errs.append(f"{rel}: could not read ({e})")
                continue
            hit = EMAIL_RE.search(text)
            if hit:
                errs.append(f"{rel}: looks like an email address ('{hit.group()}') - remove all PII")

    if not present_csvs:
        errs.append("no metric CSV found - include at least one of physiological_cycles/sleeps/workouts.csv")

    # --- metadata ---
    meta_path = folder / "metadata.yml"
    if not meta_path.exists():
        errs.append("missing metadata.yml (copy contributions/_TEMPLATE/metadata.yml)")
        return errs

    meta = parse_metadata(meta_path.read_text(encoding="utf-8", errors="replace"))

    for key in REQUIRED_KEYS:
        if not meta.get(key):
            errs.append(f"metadata.yml: missing or empty required key '{key}'")

    for key in REQUIRED_TRUE:
        if meta.get(key) is not True:
            errs.append(f"metadata.yml: '{key}' must be set to true")

    pseudo = meta.get("pseudonym")
    if pseudo and str(pseudo).strip().lower() != name.lower():
        errs.append(f"metadata.yml: pseudonym '{pseudo}' must match the folder name '{name}'")
    if isinstance(pseudo, str) and "xxxx" in pseudo.lower():
        errs.append("metadata.yml: pseudonym still says 'user-XXXX' - set a real pseudonym")

    devices = meta.get("devices")
    if isinstance(devices, list):
        for d in devices:
            norm = "MG" if str(d).strip().upper() == "MG" else str(d).strip()
            if norm not in ALLOWED_DEVICES:
                errs.append(f"metadata.yml: device '{d}' is not one of {sorted(ALLOWED_DEVICES)}")
    elif devices:
        errs.append("metadata.yml: 'devices' must be a list (e.g. - \"5.0\")")

    dr = meta.get("date_range")
    if isinstance(dr, dict):
        for edge in ("start", "end"):
            val = str(dr.get(edge, "")).strip()
            if not DATE_RE.match(val):
                errs.append(f"metadata.yml: date_range.{edge} must be YYYY-MM-DD (got '{val}')")

    files = meta.get("files")
    if isinstance(files, list):
        for fn in files:
            if "journal" in str(fn).lower():
                errs.append("metadata.yml: journal must not be listed in files")
            elif not (folder / str(fn)).exists():
                errs.append(f"metadata.yml: listed file '{fn}' is not in the folder")

    return errs


def find_folders(argv: list[str]) -> list[Path]:
    if argv:
        return [Path(a).resolve() for a in argv]
    if not CONTRIB.exists():
        return []
    return sorted(
        d for d in CONTRIB.iterdir() if d.is_dir() and not d.name.startswith("_")
    )


def main(argv: list[str]) -> int:
    # Keep output ASCII-clean regardless of console encoding (Windows cp1252 would otherwise crash).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    folders = find_folders(argv)
    if not folders:
        print("No contribution folders to validate.")
        return 0

    total_errs = 0
    for folder in folders:
        if not folder.exists():
            print(f"FAIL {folder}: does not exist")
            total_errs += 1
            continue
        errs = validate_folder(folder)
        if errs:
            total_errs += len(errs)
            print(f"FAIL {folder.name}:")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"OK   {folder.name}")

    print()
    if total_errs:
        print(f"FAILED - {total_errs} problem(s). Fix them and push again. See CONTRIBUTING.md.")
        return 1
    print("All contributions valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
