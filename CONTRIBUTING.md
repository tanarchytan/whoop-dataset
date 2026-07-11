# Contributing your WHOOP data

Thanks for helping build an open WHOOP dataset. Please read this fully — especially the
**[safety rules](#safety-rules-read-first)** — before opening a PR.

## Safety rules (read first)

1. 🚫 **Never include `journal_entries.csv`.** It holds free-text behaviour logs that can contain
   sensitive personal information. PRs containing it are rejected automatically.
2. 🚫 **No screenshots, PDFs, profile files, or the raw account file** — only the three metric CSVs.
3. 🔒 **No emails or personal data.** Whether you go anonymous or use your username, never put an
   **email address** or other personal data anywhere, including `metadata.yml`.
4. ✅ **Only your own data.** Contribute data about yourself that you consent to publishing publicly.

The dataset is published under **CC BY 4.0** (see [`LICENSE`](LICENSE)).

## Step-by-step

### 1. Export your WHOOP data

In the WHOOP app: **Menu → App Settings → Data Export → Download my data**. WHOOP emails you a ZIP.
Unzip it — you'll see files like `physiological_cycles.csv`, `sleeps.csv`, `workouts.csv`, and
`journal_entries.csv`.

### 2. Remove the journal

**Delete `journal_entries.csv`.** This is the single most important step. Keep only:

- `physiological_cycles.csv`
- `sleeps.csv`
- `workouts.csv`

(If a file is missing from your export — e.g. you have no workouts — just include the ones you have.)

### 3. Create your contribution folder

Folders are sorted **by device, then by you**: `contributions/<device>/<name>/`.

- `<device>`: your WHOOP model — `3.0`, `4.0`, `5.0`, or `mg`.
- `<name>`: a **username** (e.g. `alex`) **or** an **anonymous id** (e.g. `user-0001`) — your choice.
  If you go anonymous and want to avoid collisions, add a short suffix (`user-3f9a`).

```
contributions/5.0/user-0001/
```

If your data spans more than one WHOOP model, make a folder under each device with that device's data.
Drop your three CSVs into your folder.

### 4. Fill in `metadata.yml`

Copy [`contributions/_TEMPLATE/metadata.yml`](contributions/_TEMPLATE/metadata.yml) into your folder
and fill it in. Minimum required:

```yaml
username: user-0001            # must match your folder name (a username, or an anon id)
device: "5.0"                  # must match the parent device folder: 3.0 | 4.0 | 5.0 | mg
date_range:
  start: "2023-06-01"           # first cycle date (YYYY-MM-DD)
  end:   "2024-12-31"           # last cycle date
files:
  - physiological_cycles.csv
  - sleeps.csv
  - workouts.csv
journal_excluded: true          # journal_entries.csv is NOT included
consent_public: true            # your own data, consented to public CC BY 4.0
anonymized: true                # true = anon id (user-0001); false = your real username
```

Optional, non-identifying context that makes the data more useful (all optional — leave blank to omit):
`timezone`, `sex`, `age_band` (a band like `30-39`, never an exact birth date), `notes`.

### 5. Open a pull request

Open a PR against `main`. The PR template has a checklist — tick every box honestly. A GitHub Action
runs [`scripts/validate_contribution.py`](scripts/validate_contribution.py) and will flag:

- a `journal*` file,
- disallowed file types,
- an email address (or other obvious PII) anywhere in your files,
- a missing/incomplete `metadata.yml` (or a `device` that doesn't match the folder),
- a wrong/unknown device folder,
- unmet required confirmations.

Fix anything it reports and push again.

## Running the check locally (optional)

```bash
python3 scripts/validate_contribution.py               # checks all contributions
python3 scripts/validate_contribution.py contributions/5.0/user-0001   # just yours
```

Pure standard-library Python 3 — no `pip install` needed.

## Removing your data later

Changed your mind? Open an issue (or a PR deleting your folder) and we'll remove it.
