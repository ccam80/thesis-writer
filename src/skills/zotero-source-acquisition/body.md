# Zotero Source Acquisition

Find sources the author's Zotero library lacks, and import the ones the author approves. Do not research, synthesize, plan, or write.

Read [records.md](references/records.md) before staging candidates. Use `scripts/zotero_import.py` for every library check and every import, and run it yourself; never hand the author a command to run. Pass paths with forward slashes.

## Requests

A request describes what the author needs: a fact, a document, or a kind of source, with any constraints on source type or authority. It should also list the items `zotero-research` has already found for the same need. A request needs no identifier.

Ask the caller to clarify a request too vague to search for. Do not interpret evidence or judge whether a source supports a claim.

## Discover

1. Use one dedicated acquisition profile outside the user's normal Chrome profile. Start a headed installed Google Chrome with `--remote-debugging-address=127.0.0.1`, a fixed localhost debugging port, and `--user-data-dir=<dedicated-profile>`, and connect Playwright to it with `chromium.connect_over_cdp`. Never launch Playwright Chromium for authenticated publisher access.
2. When a site needs authentication, SSO, 2FA, consent, or a CAPTCHA, bring its tab to the foreground, tell the author which site needs attention, and wait. Never enter, request, capture, or log credentials, one-time codes, or challenge answers. Leave those tabs open.
3. Search for authoritative primary sources: publisher versions, standards, official manuals, manufacturer documentation, or official datasets. Use aggregators only to find the canonical source.
4. Skip any item the request says research already found.
5. Capture metadata from the canonical record. Resolve DOI redirects, and keep both the DOI and the non-secret landing URL.
6. Download the PDF only where access is lawful. Confirm it is a readable PDF, and check its identity against the metadata: a DOI printed in the PDF, or close title agreement with matching creator or year. Record the verdict as `match`, `weak`, `mismatch`, or `unreadable`. Drop a `mismatch`. The importer refuses anything but `match`, so show a `weak` or `unreadable` candidate to the author only to ask whether to look for a better copy.
7. Write the batch file.
8. Run `zotero_import.py --batch <file> --check`, with the same key options as the import below. Remove every candidate it reports as a duplicate, and tell the author which library item already holds each one. A different version or edition of a work the library holds counts as a duplicate unless the author asked for that version; then set `allow_similar` and check again.

Never record or echo a URL that carries an authentication code, SAML payload, session identifier, access token, cookie, or expiring signature. Where the visible PDF tab has a signed URL, record the canonical landing page instead.

## Present and approve

Present the remaining candidates once, in a compact table: ID, title, issuer or authors, year, DOI or URL, identity verdict, and what need it answers. Leave each candidate's landing page open in a tab for the author to inspect. Say that nothing has been imported and that no candidate is evidence yet.

Import only after the author approves. Approval may name candidate IDs, or cover the whole table ("yes", "import them all"). An approval relayed by the coordinating agent counts when it quotes or restates the author's words. Ask again only when the author's reply is ambiguous about which candidates it covers.

## Import

Run:

```text
python scripts/zotero_import.py --batch <file> --approve <IDs or all> --journal-dir <dir> --keyring-service <service> --keyring-username <user>
```

Name an environment variable with `--api-key-env` only when the author configured that fallback.

The script validates every approved candidate before writing anything. It then checks the API key's write and file access, and imports each candidate as its own transaction: it skips a duplicate, creates the parent item and the attachment, uploads the PDF, and verifies both items by fetching them back. If a stage fails after the parent item exists, it deletes the attachment and then the parent, and confirms both deletions. A rollback it cannot confirm stops the batch. Do not reproduce or bypass any of this in your own HTTP code.

Never log request headers, response bodies, storage URLs, upload keys, cookies, signed URLs, or API keys.

## Report and hand off

Report one line per candidate: imported with its parent and attachment keys, skipped as a duplicate of an existing item, rolled back with the reason, or `rollback-incomplete` with the created keys and the manual clean-up needed. List the review tabs still open by canonical URL, and do not close them.

An imported item is not evidence. Once the author's indexing has run, hand the new items and the original need back to `zotero-research` for a quick check. Only that check can say whether a source supports anything.
