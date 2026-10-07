# Acquisition records

`scripts/zotero_import.py` reads one batch file and writes one journal per imported candidate. Serialize both as JSON.

## Batch file

```json
{
  "schema": "zotero-source-batch/v2",
  "target": {
    "library_type": "user",
    "library_id": "<non-secret library ID>",
    "collection_key": "<optional>"
  },
  "candidates": [
    {
      "candidate_id": "SRC-0001",
      "need": "<what the author needs this source to show>",
      "authority_class": "publisher-primary | standard | official-manual | manufacturer-documentation | official-dataset",
      "relevance_note": "<bibliographic scope only; no support verdict>",
      "allow_similar": false,
      "metadata": {
        "itemType": "journalArticle",
        "title": "<canonical title>",
        "creators": [{"creatorType": "author", "firstName": "<given>", "lastName": "<family>"}],
        "publicationTitle": "<journal or issuing body>",
        "date": "<published date>",
        "DOI": "<normalized DOI without https://doi.org/>",
        "url": "<canonical non-secret landing URL>",
        "accessDate": "<ISO-8601 UTC timestamp>"
      },
      "pdf": {
        "local_path": "<absolute staged path, forward slashes>",
        "filename": "<filename.pdf>"
      },
      "pdf_identity": {
        "verdict": "match | weak | mismatch | unreadable",
        "detail": "<non-secret explanation>"
      },
      "review_tab": "<canonical article or document landing URL>"
    }
  ]
}
```

Assign candidate IDs in order within a batch and never reuse one for a different source. Optional metadata fields such as `volume`, `issue`, and `pages` follow Zotero's field names.

`relevance_note` may describe title, abstract, source type, issuer, date, and apparent topic. It must not say that the source supports, contradicts, qualifies, establishes, or proves anything.

Set `allow_similar` to `true` only when the author asks for a version of a work whose title is similar to one the library already holds. A matching DOI or URL is still treated as a duplicate.

## Check output

`--check` prints one entry per candidate:

```json
[{"candidate_id": "SRC-0001", "state": "new", "existing_item_key": null}]
```

`state` is `new` or `duplicate`; a duplicate names the library item that holds the work.

## Import outcome

Import prints one entry per approved candidate. `state` is one of:

- `imported-unindexed`, with `parent_item_key` and `attachment_key`;
- `skipped-duplicate`, with `existing_item_key`;
- `rolled-back`, with the failed `operation` and `message`;
- `rollback-incomplete`, with the `operation`, `message`, and whatever `parent_item_key` and `attachment_key` were created;
- `failed`, when the failure came before anything was created;
- `not-attempted`, for candidates after a `rollback-incomplete`.

## Import journal

The importer writes `<journal-dir>/<candidate_id>.json` atomically at every stage. It records the candidate ID, the PDF's SHA-256, the target library, the created or existing item keys, each stage's state, the rollback state, and a sanitized failure. It never stores API keys, cookies, authorization headers, upload parameters, upload keys, signed storage URLs, SSO payloads, or response bodies.
