# Acquisition records

Use these records as the machine-checkable boundary between discovery, approval, Zotero mutation, and research. Serialize them as YAML or JSON without omitting required fields.

## Candidate record

```yaml
schema: zotero-source-candidate/v1
candidate_id: SRC-0001
state: candidate
claim_ids: [C-3.2-P1-04]
gap_receipt:
  research_run_id: <stable receipt from zotero-research>
  verdict: corpus-gap
candidate_basis:
  authority_class: publisher-primary | standard | official-manual | manufacturer-documentation | official-dataset
  relevance_note: <bibliographic scope only; no support verdict>
metadata:
  itemType: journalArticle
  title: <canonical title>
  creators:
    - creatorType: author
      firstName: <given names>
      lastName: <family name>
  publicationTitle: <journal or issuing body>
  date: <published date>
  volume: <optional>
  issue: <optional>
  pages: <optional>
  DOI: <normalized DOI without https://doi.org/>
  url: <canonical non-secret landing URL>
  accessDate: <ISO-8601 UTC timestamp>
pdf:
  local_path: <absolute staged path>
  filename: <approved filename.pdf>
  sha256: <lowercase hex>
  byte_count: <integer>
  magic: "%PDF-"
pdf_identity:
  verdict: match | weak | mismatch | unreadable
  signals:
    doi: match | absent | mismatch
    title_token_fraction: <0.0 to 1.0>
    creator_year: match | absent | mismatch
  detail: <non-secret explanation>
review_tab:
  url: <canonical article/document landing URL>
  left_open: true
target:
  library_type: user | group
  library_id: <non-secret library ID>
  collection_key: <optional>
record_sha256: <hash of candidate ID, claim IDs, canonical metadata, target, PDF filename/SHA-256, and PDF identity record>
created_at: <ISO-8601 UTC timestamp>
```

Assign candidate IDs monotonically within an acquisition run. Never recycle an ID for a different source. Keep rejected records with `state: rejected` so an old approval cannot select a replacement accidentally.

The `relevance_note` may describe title, abstract, source type, issuer, date, and apparent topic. It must not say that the source supports, contradicts, qualifies, establishes, or proves any claim.

## Approval record

```yaml
schema: zotero-source-approval/v1
approved_candidate_ids: [SRC-0001]
approved_record_sha256:
  SRC-0001: <candidate record_sha256>
approval_text: "Approve import: SRC-0001"
approved_at: <ISO-8601 UTC timestamp>
```

Record only explicit user text naming exact candidate IDs. Invalidate this record when any corresponding `record_sha256` changes.

## Import journal

```yaml
schema: zotero-source-import/v1
candidate_id: SRC-0001
approved_record_sha256: <exact approved hash>
state: approved-for-import | parent-created | attachment-created | storage-uploaded | imported-unindexed | rollback-required | rolled-back | rollback-incomplete
target:
  library_type: user | group
  library_id: <non-secret library ID>
zotero:
  parent_item_key: <safe key or null>
  attachment_key: <safe key or null>
stages:
  access_preflight: pending | complete | failed
  deduplicate: pending | complete | failed
  parent_create: pending | complete | failed
  attachment_create: pending | complete | failed
  upload_authorize: pending | complete | exists | failed
  storage_upload: pending | complete | skipped-existing | failed
  upload_register: pending | complete | skipped-existing | failed
  fetchback_verify: pending | complete | failed
rollback:
  attachment_delete: not-required | pending | confirmed | failed
  parent_delete: not-required | pending | confirmed | failed
failure:
  operation: <safe operation name or null>
  status_code: <integer or null>
  message: <sanitized message or null>
updated_at: <ISO-8601 UTC timestamp>
```

Write the parent key before attachment creation. Write the attachment key before requesting upload authorization. Never store API keys, cookies, authorization headers, upload parameters, upload keys, signed storage URLs, SSO payloads, or response bodies in the journal.

## Indexing handoff

```yaml
schema: zotero-source-indexing-handoff/v1
candidate_id: SRC-0001
claim_ids: [C-3.2-P1-04]
library_type: user
library_id: <library ID>
parent_item_key: <Zotero parent key>
attachment_key: <Zotero attachment key>
title: <approved title>
DOI: <normalized DOI>
state: imported-unindexed
```

Accept an indexing result only when it names the same library, parent key, and attachment key. Pass that receipt to `zotero-research`; do not translate it into an evidence verdict.
