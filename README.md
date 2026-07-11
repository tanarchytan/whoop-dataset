# whoop-dataset

An **open, community-contributed dataset** of WHOOP data. People export their own WHOOP data and
add it here through a pull request, so researchers, tinkerers, and app developers have real,
multi-device WHOOP metrics to work with.

> [!CAUTION]
> **Never add your `journal_entries.csv`.** The journal contains free-text behaviour logs (alcohol,
> caffeine, medications, illness, mental-health notes, and more) — it is the one export file that can
> hold genuinely sensitive personal information. It is **not** wanted here and PRs that include it are
> automatically rejected. See [What to exclude](#what-to-exclude).

This is a **wellness dataset, not a medical one.** WHOOP metrics are consumer wellness estimates; treat
them as such. Nothing here is medical advice or diagnostic data.

---

## What a WHOOP export looks like

You get your data from the WHOOP app: **Menu → App Settings → Data Export → Download my data** (WHOOP
emails you a ZIP). A typical export contains these CSV files (exact names can vary slightly by export
version):

| File | Contents | Add it? |
|---|---|---|
| `physiological_cycles.csv` | Per-day cycle: recovery %, RHR, HRV, skin temp, SpO₂, day strain, energy, sleep summary | ✅ yes |
| `sleeps.csv` | Per-sleep: onset/wake, stages (light/deep/REM/awake), efficiency, need, debt, respiratory rate | ✅ yes |
| `workouts.csv` | Per-workout: activity, strain, HR zones, energy, distance, altitude | ✅ yes |
| `journal_entries.csv` | Free-text behaviour/journal answers | 🚫 **never** — see caution above |

So a valid contribution is **the three green CSVs, anonymised** — nothing else.

## What this dataset is (and isn't)

- **Is:** per-day / per-night / per-workout **aggregate metrics** across many people and WHOOP
  generations. Great for cross-person recovery/sleep/strain analysis, model building, and app testing.
- **Isn't:** raw beat-to-beat R‑R intervals or raw sensor samples. WHOOP's export is aggregate; if you
  need signal-level data, this isn't the source.

## Supported devices

Tell us which WHOOP generation(s) the data came from — one export can span several as people upgrade:

- `3.0`
- `4.0`
- `5.0`
- `MG` (WHOOP MG)

## Anonymisation (required)

Every contribution must be anonymised:

- Your folder is a **pseudonym** — `user-01`, `user-3f9a`, etc. — **never your real name or handle**.
- Remove any name / email / identifying field from the files. In practice the three metric CSVs don't
  carry your name, but you are responsible for confirming there's no personal identifier left.
- `metadata.yml` carries **no** real name — only the pseudonym plus optional, non-identifying context.

You confirm this with a tick-box on the PR (and CI double-checks it — e.g. it fails on an email
address or a `journal` file).

## How to contribute

Full steps are in **[CONTRIBUTING.md](CONTRIBUTING.md)**. In short:

1. Export your WHOOP data and unzip it.
2. **Delete `journal_entries.csv`.**
3. Make a folder `contributions/user-XXXX/` (a pseudonym) and drop in the three CSVs.
4. Fill in `metadata.yml` (copy [`contributions/_TEMPLATE/metadata.yml`](contributions/_TEMPLATE/metadata.yml)).
5. Open a pull request and tick the boxes in the PR template.

Automated checks run on every PR (see [`scripts/validate_contribution.py`](scripts/validate_contribution.py)).

## Repository layout

```
whoop-dataset/
├── README.md
├── CONTRIBUTING.md
├── LICENSE                      # dataset license (CC BY 4.0)
├── schema/
│   └── DATA_DICTIONARY.md       # what each CSV column means
├── scripts/
│   └── validate_contribution.py # structure + safety checks (stdlib only)
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/validate.yml   # runs the validator on every PR
└── contributions/
    ├── _TEMPLATE/               # copy this folder to start
    │   ├── metadata.yml
    │   └── PLACE_YOUR_CSVS_HERE.md
    └── user-XXXX/               # one folder per contributor (pseudonym)
        ├── metadata.yml
        ├── physiological_cycles.csv
        ├── sleeps.csv
        └── workouts.csv
```

## License & consent

The dataset is published under **[CC BY 4.0](LICENSE)** — free to use with attribution. By opening a
PR you confirm the data is **your own** and that you **consent to publishing it publicly**. You can
ask for your contribution to be removed at any time by opening an issue.

*(Maintainer note: CC BY 4.0 is the default; open an issue if you think CC0 / public-domain would serve
the dataset better.)*

## Disclaimer

Not affiliated with or endorsed by WHOOP. "WHOOP" is a trademark of its owner. This repository contains
only data that individuals chose to export and share about themselves. Wellness estimates only — not
medical data.
