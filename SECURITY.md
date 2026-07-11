# Reporting a data concern

This repository contains only data that individuals chose to export and share about themselves. If you
believe a contribution contains **personal or sensitive information** — an email, a real name, a
`journal` file, free-text notes, or anything that could identify a person — please tell us:

- Open a **[Report sensitive or personal data](../../issues/new?template=report-sensitive-data.md)**
  issue, **or**
- If you'd rather not do it publicly, contact the maintainer privately.

> **Please do not paste the sensitive value** into a public issue — just point to the file. We'll
> remove or redact it promptly.

## For contributors

- Only contribute data about **yourself**, with your consent.
- **Never** include `journal_entries.csv` or any file with a name containing "journal".
- Use a pseudonym (`user-XXXX`), never your real name/handle.
- You can request removal of your own data at any time via the **Remove my data** issue.

## Automated safeguards

Every pull request is checked by [`scripts/validate_contribution.py`](scripts/validate_contribution.py)
(via GitHub Actions), which rejects journal files, email addresses, disallowed file types, and
incomplete metadata. Branch protection requires that check to pass and a maintainer review before any
change reaches `main`. Automation is a backstop, not a guarantee — human vigilance still matters, hence
this reporting path.
