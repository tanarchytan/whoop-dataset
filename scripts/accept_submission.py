#!/usr/bin/env python3
"""Maintainer helper: turn a data-submission ZIP (from an "Add my WHOOP data" issue) into a
validated contribution folder, in one command.

    python3 scripts/accept_submission.py --zip ~/Downloads/data.zip \
        --device 5.0 --user user-0002 --start 2023-06-01 --end 2024-12-31 [--named] [--tz Europe/Amsterdam]

It extracts ONLY physiological_cycles.csv / sleeps.csv / workouts.csv from the ZIP (it refuses the
journal and anything else), writes metadata.yml from the flags, then runs the validator. Then you
review, commit, and close the issue. Standard library only.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRIB = ROOT / "contributions"
METRIC_CSVS = {"physiological_cycles.csv", "sleeps.csv", "workouts.csv"}
ALLOWED_DEVICES = {"3.0", "4.0", "5.0", "mg"}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Accept a WHOOP data-submission ZIP into the dataset.")
    ap.add_argument("--zip", required=True, help="path to the submitted .zip")
    ap.add_argument("--device", required=True, help="3.0 | 4.0 | 5.0 | mg")
    ap.add_argument("--user", required=True, help="folder name: a username or an anon id like user-0002")
    ap.add_argument("--start", required=True, help="first cycle date YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="last cycle date YYYY-MM-DD")
    ap.add_argument("--named", action="store_true", help="contributor used their real username (anonymized: false)")
    ap.add_argument("--tz", default="", help="optional IANA timezone")
    ap.add_argument("--sex", default="", help="optional M|F|other")
    ap.add_argument("--age", default="", help="optional age band like 30-39")
    ap.add_argument("--notes", default="", help="optional notes")
    a = ap.parse_args()

    device = "mg" if a.device.strip().lower() == "mg" else a.device.strip()
    if device not in ALLOWED_DEVICES:
        print(f"error: --device must be one of {sorted(ALLOWED_DEVICES)}")
        return 2

    dest = CONTRIB / device / a.user
    if dest.exists():
        print(f"error: {dest.relative_to(ROOT)} already exists - refusing to overwrite")
        return 2
    dest.mkdir(parents=True)

    included: list[str] = []
    with zipfile.ZipFile(a.zip) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            base = Path(info.filename).name.lower()  # basename only - zip-slip guard
            if "journal" in base:
                print(f"  SKIP (journal, may be sensitive): {info.filename}")
                continue
            if base not in METRIC_CSVS:
                print(f"  SKIP (not a metric CSV): {info.filename}")
                continue
            with z.open(info) as src:
                (dest / base).write_bytes(src.read())
            included.append(base)
            print(f"  added: {base}")

    if not included:
        print("error: no metric CSV found in the ZIP - nothing added")
        return 2

    lines = [
        f"username: {a.user}",
        f'device: "{device}"',
        "",
        "date_range:",
        f'  start: "{a.start}"',
        f'  end:   "{a.end}"',
        "",
        "files:",
        *[f"  - {f}" for f in sorted(included)],
        "",
        "journal_excluded: true",
        "consent_public: true",
        f"anonymized: {'false' if a.named else 'true'}",
    ]
    for key, val in (("timezone", a.tz), ("sex", a.sex), ("age_band", a.age), ("notes", a.notes)):
        if val:
            lines.append(f'{key}: "{val}"')
    (dest / "metadata.yml").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"  wrote {(dest / 'metadata.yml').relative_to(ROOT)}")

    # Validate in-process (same checks CI runs).
    sys.path.insert(0, str(ROOT / "scripts"))
    import validate_contribution as v  # noqa: E402

    print("\nValidating...")
    errs = v.validate_folder(dest)
    label = f"{device}/{a.user}"
    if errs:
        print(f"FAIL {label}:")
        for e in errs:
            print(f"    - {e}")
        print("\nFix the folder, then `git add` + commit. (Data was extracted but did not pass checks.)")
        return 1
    print(f"OK   {label}\n\nReview it, then:\n  git add contributions/{device}/{a.user}\n  git commit -m 'data: add {label}'\n  git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
