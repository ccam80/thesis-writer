---
name: zotero-source-acquisition
description: "Acquire authoritative sources for thesis claim IDs that Zotero research could not adequately evidence. Use only as an isolated agent after zotero-research reports a corpus gap: discover candidate sources through a headed, persistent real-Chrome SSO session; stage inspectable metadata and identity-verified PDFs; obtain explicit approval for exact candidate IDs; then create Zotero parent items and upload verified PDFs through the Zotero API before handing the new keys to indexing and zotero-research. Never use this skill to interpret evidence, support claims, write plans, or bypass Zotero-first research."
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Zotero Source Acquisition

Operate as a separate, isolated acquisition agent. Fill declared Zotero corpus gaps without becoming a research, synthesis, planning, or writing agent.

Read [records.md](references/records.md) before staging candidates or mutating Zotero. Treat its record formats and state transitions as mandatory interfaces.

Use `scripts/zotero_import.py` for validation and every approved Zotero import. Do not reimplement the transaction in ad hoc agent code. Run its `--dry-validate` mode before presenting an import as ready; invoke mutation mode only after the approval gate below.

## Accept only bounded requests

Require each request to contain:

- one or more stable claim IDs;
- the proposed claim or research question associated with each ID;
- the Zotero search receipt and gap verdict from `zotero-research`;
- source-type and authority constraints, if any;
- the target Zotero library and optional collection, without credentials.

Reject requests to invent claims, expand a plan, select prose, verify support, or search externally before Zotero research has recorded a gap. Return malformed or unbounded requests to the caller.

## Preserve the epistemic boundary

- Discover candidate sources; do not state that a candidate supports, contradicts, qualifies, or proves a claim.
- Report bibliographic relevance only: title/abstract keywords, document type, issuer, date, and apparent scope.
- Do not quote candidate passages as evidence and do not update any thesis plan, claim card, prose, bibliography, or citation mapping.
- Do not assign a Better BibTeX key. Only Zotero/indexing may establish the corpus identity used by research.
- Mark every output `candidate`, `approved-for-import`, `imported-unindexed`, `indexed`, or `failed`; never call a discovered source `evidence`.
- Hand imported sources back to indexing and then to `zotero-research`. Only that research agent may inspect the indexed text and issue an evidence verdict.

## Phase 1: Discover and stage candidates

Perform this phase without Zotero mutation.

1. Create or reuse one dedicated acquisition profile outside the user's normal Chrome profile.
2. Start a headed installed Google Chrome process with `--remote-debugging-address=127.0.0.1`, a fixed localhost debugging port, and `--user-data-dir=<dedicated-profile>`.
3. Connect Playwright to `http://127.0.0.1:<port>` using `chromium.connect_over_cdp`. Never launch Playwright Chromium for authenticated publisher access.
4. If authentication, SSO, 2FA, consent, or CAPTCHA is required, bring the relevant headed tab to the foreground and pause. Tell the user what site needs attention. Never enter, request, capture, or log credentials, one-time codes, recovery codes, or challenge answers.
5. Leave pending CAPTCHA and authentication tabs open for the user. Leave every shortlisted candidate's canonical article or document landing page open for review. Do not close user-visible review tabs, popups needed for authentication, or the real Chrome process when disconnecting Playwright.
6. Search for authoritative primary sources appropriate to the gap: publisher versions, standards bodies, official manuals, manufacturer documentation, or official datasets. Use aggregators only to locate the canonical source.
7. Capture bibliographic metadata from the canonical record. Resolve DOI redirects to a canonical DOI, but store both DOI and non-secret landing URL where available.
8. Obtain a PDF only when access is lawful and the session permits it. Validate `%PDF-` magic bytes, MIME where available, nontrivial size, and readable PDF structure.
9. Verify PDF identity against the staged metadata. Prefer DOI printed in the PDF; otherwise require strong normalized-title agreement and corroborating creator/year metadata. Classify `match`, `weak`, `mismatch`, or `unreadable`. Never stage `mismatch`; stage `weak` or `unreadable` only for explicit human review and prohibit import until the verdict becomes `match`.
10. Compute a SHA-256 digest of the staged PDF and store it with its local path. Do not store PDF bytes in the record.
11. Assign a stable candidate ID and write a candidate record using [records.md](references/records.md). Associate every candidate with the claim IDs whose gap triggered discovery.
12. Present the candidate register to the user. Include the exact candidate IDs, canonical metadata, DOI/URL, PDF identity verdict, safe review-tab URL, and claim IDs. State that no candidate has been imported and no evidence verdict has been made.

Use the shortest canonical review URL. Never record or echo URLs containing authentication codes, SAML payloads, session identifiers, access tokens, cookies, or expiring signatures. If the visible PDF tab uses a signed URL, keep the tab open but record the canonical landing-page tab instead.

## Approval gate

Stop after staging. Import nothing until the user explicitly approves exact candidate IDs, for example: `Approve import: SRC-0002, SRC-0005`.

- Treat approval of a topic, claim, search, publisher, or general candidate list as insufficient.
- Import only the named IDs. Do not infer approval for alternates, revised metadata, or additional PDFs.
- Freeze the approved record by hashing its canonical metadata plus PDF SHA-256. If metadata, file identity, parent type, target library, or PDF changes after approval, invalidate approval and present the changed candidate for approval again.
- Require `pdf_identity.verdict: match` and a locally revalidated PDF digest immediately before import.

## Phase 2: Import approved candidates

Run each approved candidate as an independent transaction. Never perform import during discovery.

1. Compute the candidate's canonical record hash before requesting approval:
   `python scripts/zotero_import.py --candidate candidate.json --compute-record-hash`
2. Put that hash in both the candidate and exact-ID approval records.
3. Run the non-mutating gate:
   `python scripts/zotero_import.py --candidate candidate.json --approval approval.json --dry-validate`
4. After validation and explicit approval, run the importer with a journal path and keyring coordinates. Name an environment variable with `--api-key-env` only when the user explicitly configured that fallback.
5. Treat a duplicate result as a stop condition. Ask whether the existing item should be handled in a separately approved operation; do not auto-attach.
6. Return the parent and attachment keys emitted by the script. Do not infer success if its journal does not end at `imported-unindexed`.

The script owns metadata/PDF hash revalidation, a `/keys/current` preflight for target-library write and file access, conservative pre-mutation deduplication, parent and attachment creation, the Zotero v3 file handshake, fetchback verification, atomic secret-free journaling, and ordered rollback. Do not reproduce or bypass those operations in agent-authored HTTP code.

For the upload-authorization step, treat only a successful `200` response containing `{"exists": 1}` as existing content. A `412` response is a precondition failure, not success.

Never log request headers, response bodies that may contain upload credentials, storage URLs, upload keys, cookies, signed URLs, or API keys. Sanitize exception text to status code, operation name, candidate ID, and safe Zotero item keys.

## Roll back required-stage failures

Let `scripts/zotero_import.py` journal each created key before starting the next stage. If any required stage after parent creation fails, require it to:

1. Mark the journal transaction `rollback-required`.
2. Delete the created attachment first when an attachment key exists.
3. Confirm the attachment no longer exists.
4. Delete the created parent second.
5. Confirm the parent no longer exists.
6. Mark `rolled-back` only after both confirmations.

If rollback cannot be confirmed, stop. Return `rollback-incomplete`, the safe parent and attachment keys, the failed deletion stage, and the manual recovery action. Never suppress or replace these keys. Do not roll back pre-existing Zotero items. Do not process the next candidate while the current transaction is rollback-incomplete.

## Handoff

For every successful import, send the indexing service or indexing agent:

- candidate ID and triggering claim IDs;
- Zotero library identity;
- parent item key and attachment key;
- approved title and DOI;
- state `imported-unindexed`.

Wait for an indexing receipt tied to the parent/attachment keys. Then hand the claim IDs and newly indexed Zotero item identity to `zotero-research` for a fresh bounded search. Do not claim the gap is resolved until `zotero-research` returns claim-centred passages and a support, qualification, contradiction, or remaining-gap verdict.

## Return contract

Return one of these outcomes per candidate:

- `candidate`: staged for user review; no Zotero mutation;
- `approved-for-import`: approval recorded but import not yet attempted;
- `imported-unindexed`: parent and verified PDF attachment created; include both keys;
- `indexed`: include the indexing receipt and research handoff status;
- `failed`: include the safe stage, reason, rollback status, and created keys if recovery is incomplete.

Always include a compact summary of open review tabs by safe canonical URL. Never close those tabs as part of completion.
