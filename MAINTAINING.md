# Maintaining the dataset

## Accepting an "Add my WHOOP data" issue

When someone submits data through the **Add my WHOOP data** issue form:

1. **Download** the `.zip` they attached to the issue.
2. **Run the helper** — it extracts *only* the three metric CSVs, refuses any journal file, writes
   `metadata.yml` from the issue fields, and runs the validator:

   ```bash
   python3 scripts/accept_submission.py --zip ~/Downloads/data.zip \
       --device 5.0 --user user-0002 --gh-user theirLogin \
       --start 2023-06-01 --end 2024-12-31 [--named] [--tz Europe/Amsterdam]
   ```

   - `--device` one of `3.0 | 4.0 | 5.0 | mg` (from the form's device dropdown)
   - `--user` the handle they chose (their username, or an anon id like `user-0002`)
   - `--gh-user` **the GitHub login of the issue author** — always pass this (see below)
   - `--named` if they chose "Named (my username)" — sets `anonymized: false`
   - `--tz` / `--sex` / `--age` / `--notes` optional extras

   It prints `OK <device>/<user>-<tag>` when the contribution passes, and the exact `git` commands to run.

   ### Why `--gh-user` — preventing handle collisions

   The handle in `--user` is whatever the contributor typed, so two different people can both pick
   `user-69`. To keep them apart, the script appends a short **owner tag** — 4 hex derived from the
   issue author's GitHub login — to the folder name: `user-69` → `user-69-7e79`.

   - **Same person, same login → same tag.** A re-submission lands on the same folder, so the script
     recognises it and refuses to silently overwrite.
   - **Different person, same handle → different tag.** `user-69-7e79` and `user-69-a1b2` coexist; no
     collision.
   - **One-way + provable.** The login is never stored — only the hash (also written as `owner_tag` in
     `metadata.yml`). You can re-derive it from a claimed login to prove folder ownership (see removal).

   The login is public on the issue anyway, so this adds no new PII; it just gives every folder a stable,
   pseudonymous owner key. If you skip `--gh-user`, the script warns and adds no tag.

3. **Eyeball the CSVs** for anything the automated PII scan can't catch (odd free-text, a stray name).
4. **Commit + push:**

   ```bash
   git add contributions/5.0/user-0002-3f9a
   git commit -m "data: add 5.0/user-0002-3f9a (issue #NN)"
   git push
   ```

5. **Close the issue**, linking the commit.

The `validate` check also runs on push to `main`, so a mistake is caught there too.

## Handling a "Report sensitive or personal data" issue

Treat as urgent. Redact or remove the flagged file/folder (a small PR or a direct commit), then close
the issue. Never quote the sensitive value in a public comment.

## Removing a contribution on request

Delete the contributor's folder (`contributions/<device>/<name>/`) and push. Confirm the requester
owns it — the folder's trailing **owner tag** re-derives from their GitHub login:

```bash
python3 -c "import hashlib,sys; print(hashlib.sha256(sys.argv[1].strip().lower().encode()).hexdigest()[:4])" theirLogin
```

If that matches the suffix on the folder (or the `owner_tag` in its `metadata.yml`), they own it. (They
opening the request from the submitting account is also proof.)
