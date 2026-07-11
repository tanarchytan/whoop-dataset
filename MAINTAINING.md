# Maintaining the dataset

## Accepting an "Add my WHOOP data" issue

When someone submits data through the **Add my WHOOP data** issue form:

1. **Download** the `.zip` they attached to the issue.
2. **Run the helper** — it extracts *only* the three metric CSVs, refuses any journal file, writes
   `metadata.yml` from the issue fields, and runs the validator:

   ```bash
   python3 scripts/accept_submission.py --zip ~/Downloads/data.zip \
       --device 5.0 --user user-0002 --start 2023-06-01 --end 2024-12-31 [--named] [--tz Europe/Amsterdam]
   ```

   - `--device` one of `3.0 | 4.0 | 5.0 | mg` (from the form's device dropdown)
   - `--user` the folder name (their username, or an anon id like `user-0002`)
   - `--named` if they chose "Named (my username)" — sets `anonymized: false`
   - `--tz` / `--sex` / `--age` / `--notes` optional extras

   It prints `OK <device>/<user>` when the contribution passes, and the exact `git` commands to run.

3. **Eyeball the CSVs** for anything the automated PII scan can't catch (odd free-text, a stray name).
4. **Commit + push:**

   ```bash
   git add contributions/5.0/user-0002
   git commit -m "data: add 5.0/user-0002 (issue #NN)"
   git push
   ```

5. **Close the issue**, linking the commit.

The `validate` check also runs on push to `main`, so a mistake is caught there too.

## Handling a "Report sensitive or personal data" issue

Treat as urgent. Redact or remove the flagged file/folder (a small PR or a direct commit), then close
the issue. Never quote the sensitive value in a public comment.

## Removing a contribution on request

Delete the contributor's folder (`contributions/<device>/<name>/`) and push. Confirm the requester
owns it (they opened the request from the submitting account, or can otherwise prove it).
