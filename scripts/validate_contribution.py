#!/usr/bin/env python3
"""Validate WHOOP dataset contributions.

Layout is sorted by device, then contributor:

    contributions/<device>/<name>/{physiological_cycles,sleeps,workouts}.csv + metadata.yml

  * <device> is one of: 3.0, 4.0, 5.0, mg
  * <name> is a GitHub-style username OR an anonymous id like user-0001 (contributor's choice)

Enforces the repo's safety + structure rules so sensitive or malformed data can't land:

  * no journal_entries.csv (or any "journal" file) - the one export file that can hold sensitive data
  * only the allowed files (the three metric CSVs + metadata.yml + optional NOTES/README)
  * no email address (or other obvious PII) anywhere in the contributed text
  * a complete metadata.yml whose device matches the folder it's in
  * required confirmations (journal_excluded, consent_public) set to true

Standard library only - no `pip install`. Run:

    python3 scripts/validate_contribution.py                          # all contributions
    python3 scripts/validate_contribution.py contributions/5.0/user-0001   # one folder
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRIB = ROOT / "contributions"

ALLOWED_DEVICES = {"3.0", "4.0", "5.0", "mg"}
METRIC_CSVS = {"physiological_cycles.csv", "sleeps.csv", "workouts.csv"}
ALLOWED_FILES = METRIC_CSVS | {"metadata.yml", "notes.md", "readme.md"}
REQUIRED_KEYS = ["username", "device", "date_range", "files"]
REQUIRED_TRUE = ["journal_excluded", "consent_public"]  # anonymized is a choice, not required

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,38}$")  # username or anon id (e.g. user-0001)
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


def _norm_device(d) -> str:
    d = str(d).strip()
    return "mg" if d.lower() == "mg" else d


def validate_folder(folder: Path) -> list[str]:
    errs: list[str] = []
    name = folder.name
    device = _norm_device(folder.parent.name)  # the parent folder IS the device

    if not NAME_RE.match(name):
        errs.append(f"folder name '{name}' must be a username or an id like 'user-0001'")
    if device not in ALLOWED_DEVICES:
        errs.append(f"parent device folder '{folder.parent.name}' is not one of {sorted(ALLOWED_DEVICES)}")

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

    uname = meta.get("username")
    if uname and str(uname).strip() != name:
        errs.append(f"metadata.yml: username '{uname}' must match the folder name '{name}'")
    if isinstance(uname, str) and "xxxx" in uname.lower():
        errs.append("metadata.yml: username still says the template placeholder - set a real value")

    meta_device = meta.get("device")
    if meta_device is not None:
        if _norm_device(meta_device) not in ALLOWED_DEVICES:
            errs.append(f"metadata.yml: device '{meta_device}' is not one of {sorted(ALLOWED_DEVICES)}")
        elif _norm_device(meta_device) != device:
            errs.append(f"metadata.yml: device '{meta_device}' must match the folder it's in ('{device}')")

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


def gather(argv: list[str]) -> tuple[list[Path], list[str]]:
    """Return (user folders to validate, top-level structural errors)."""
    if argv:
        return [Path(a).resolve() for a in argv], []
    if not CONTRIB.exists():
        return [], []
    user_dirs: list[Path] = []
    top: list[str] = []
    for dev in sorted(CONTRIB.iterdir()):
        if dev.name.startswith("_"):
            continue
        if not dev.is_dir():
            top.append(f"contributions/{dev.name}: put data under a device folder (3.0/4.0/5.0/mg)")
            continue
        if _norm_device(dev.name) not in ALLOWED_DEVICES:
            top.append(f"contributions/{dev.name}/ is not a valid device folder (use 3.0/4.0/5.0/mg)")
            continue
        for u in sorted(dev.iterdir()):
            if u.name.startswith("_"):
                continue
            if u.is_dir():
                user_dirs.append(u)
            else:
                top.append(f"contributions/{dev.name}/{u.name}: files must live inside a user folder")
    return user_dirs, top


def main(argv: list[str]) -> int:
    # Keep output ASCII-clean regardless of console encoding (Windows cp1252 would otherwise crash).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    folders, top_errors = gather(argv)
    total_errs = len(top_errors)
    for e in top_errors:
        print(f"FAIL {e}")

    if not folders and not top_errors:
        print("No contribution folders to validate.")
        return 0

    for folder in folders:
        if not folder.exists():
            print(f"FAIL {folder}: does not exist")
            total_errs += 1
            continue
        errs = validate_folder(folder)
        label = f"{folder.parent.name}/{folder.name}"
        if errs:
            total_errs += len(errs)
            print(f"FAIL {label}:")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"OK   {label}")

    print()
    if total_errs:
        print(f"FAILED - {total_errs} problem(s). Fix them and push again. See CONTRIBUTING.md.")
        return 1
    print("All contributions valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
