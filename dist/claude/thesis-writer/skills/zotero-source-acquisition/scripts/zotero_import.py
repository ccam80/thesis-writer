#!/usr/bin/env python3
"""Import approved sources and their PDFs into Zotero.

A batch file lists staged candidates. ``--check`` reports which candidates the
library already holds, so they are never presented for approval. Import mode
takes the candidate IDs the author approved, or ``all``, and imports each one as
its own transaction: a candidate the library already holds is skipped, and a
failure after creation rolls back what that candidate created.

The module exposes pure validation functions, a replaceable HTTP transport, and a
replaceable Zotero client so tests can exercise every stage without network access.
It never logs credentials, upload parameters, response bodies, or signed URLs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ImportFailure(RuntimeError):
    """An error safe to report without exposing response bodies or secrets."""

    def __init__(self, operation: str, message: str, status_code: int | None = None):
        super().__init__(message)
        self.operation = operation
        self.safe_message = message
        self.status_code = status_code


class DuplicateCandidate(ImportFailure):
    def __init__(self, item_key: str):
        super().__init__("deduplicate", f"existing Zotero parent {item_key}")
        self.item_key = item_key


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


class HttpTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes | None = None,
        timeout: float = 120.0,
    ) -> HttpResponse: ...


class UrllibTransport:
    """Small standard-library transport; inject a fake in tests."""

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes | None = None,
        timeout: float = 120.0,
    ) -> HttpResponse:
        request = Request(url, data=body, headers=dict(headers or {}), method=method)
        try:
            with urlopen(request, timeout=timeout) as response:
                return HttpResponse(
                    int(response.status), dict(response.headers.items()), response.read()
                )
        except HTTPError as exc:
            # Retain the body only inside the response for protocol parsing. Callers
            # must never place it in exceptions, journals, or console output.
            return HttpResponse(int(exc.code), dict(exc.headers.items()), exc.read())
        except URLError as exc:
            raise ImportFailure("http", f"transport error: {type(exc.reason).__name__}") from None


class ZoteroClientLike(Protocol):
    def verify_access(self) -> None: ...
    def find_duplicate(
        self, metadata: Mapping[str, Any], *, allow_similar: bool = False
    ) -> str | None: ...
    def create_parent(self, metadata: Mapping[str, Any], collection_key: str | None) -> str: ...
    def create_attachment(self, parent_key: str, filename: str) -> str: ...
    def upload_pdf(
        self,
        attachment_key: str,
        filename: str,
        content: bytes,
        stage_hook: Callable[[str, str], None],
    ) -> str: ...
    def verify_fetchback(
        self,
        parent_key: str,
        attachment_key: str,
        metadata: Mapping[str, Any],
        filename: str,
        content_md5: str,
    ) -> None: ...
    def delete_item(self, item_key: str) -> None: ...
    def item_exists(self, item_key: str) -> bool: ...


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def hash_pdf(path: Path) -> tuple[str, str, int]:
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()  # Zotero's upload protocol requires MD5.
    size = 0
    with path.open("rb") as stream:
        magic = stream.read(5)
        if magic != b"%PDF-":
            raise ImportFailure("validate-pdf", "staged file does not have PDF magic bytes")
        sha256.update(magic)
        md5.update(magic)
        size += len(magic)
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha256.update(block)
            md5.update(block)
            size += len(block)
    if size < 2048:
        raise ImportFailure("validate-pdf", "staged PDF is implausibly small")
    return sha256.hexdigest(), md5.hexdigest(), size


BATCH_SCHEMA = "zotero-source-batch/v2"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    pdf_path: Path
    pdf_sha256: str
    pdf_md5: str
    pdf_size: int
    filename: str
    metadata: Mapping[str, Any]
    allow_similar: bool


def read_pdf(candidate: Candidate) -> bytes:
    """Read the PDF once for upload, and refuse it if it changed since validation."""
    try:
        content = candidate.pdf_path.read_bytes()
    except OSError as exc:
        raise ImportFailure("validate-pdf", f"cannot reread staged PDF: {type(exc).__name__}") from None
    if content[:5] != b"%PDF-" or len(content) != candidate.pdf_size:
        raise ImportFailure("validate-pdf", "staged PDF changed before upload")
    if hashlib.sha256(content).hexdigest() != candidate.pdf_sha256:
        raise ImportFailure("validate-pdf", "staged PDF changed before upload")
    return content


def load_batch(batch: Mapping[str, Any]) -> tuple[Mapping[str, Any], list[Mapping[str, Any]]]:
    """Return the batch's target library and its candidate records."""
    if batch.get("schema") != BATCH_SCHEMA:
        raise ImportFailure("validate-batch", "unsupported batch schema")
    target = batch.get("target")
    if not isinstance(target, dict) or target.get("library_type") not in {"user", "group"}:
        raise ImportFailure("validate-batch", "target library_type is invalid")
    if not str(target.get("library_id", "")):
        raise ImportFailure("validate-batch", "target library_id is required")
    candidates = batch.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ImportFailure("validate-batch", "batch has no candidates")
    seen: set[str] = set()
    for record in candidates:
        candidate_id = record.get("candidate_id") if isinstance(record, dict) else None
        if not isinstance(candidate_id, str) or not candidate_id:
            raise ImportFailure("validate-batch", "every candidate needs a candidate_id")
        if candidate_id in seen:
            raise ImportFailure("validate-batch", f"candidate {candidate_id} appears twice")
        seen.add(candidate_id)
    return target, candidates


def select_candidates(
    candidates: list[Mapping[str, Any]], approved: str
) -> list[Mapping[str, Any]]:
    """Return the candidates named by the approval, in batch order.

    ``approved`` is ``all`` or a comma-separated list of candidate IDs. Naming an
    ID the batch does not hold is an error, so a typo never imports nothing quietly.
    """
    if approved.strip().lower() == "all":
        return list(candidates)
    wanted = [value.strip() for value in approved.split(",") if value.strip()]
    if not wanted:
        raise ImportFailure("validate-approval", "no candidate IDs were approved")
    known = {record["candidate_id"] for record in candidates}
    unknown = sorted(set(wanted) - known)
    if unknown:
        raise ImportFailure("validate-approval", f"approval names unknown candidates: {', '.join(unknown)}")
    return [record for record in candidates if record["candidate_id"] in set(wanted)]


def validate_candidate(record: Mapping[str, Any]) -> Candidate:
    candidate_id = str(record.get("candidate_id"))
    identity = record.get("pdf_identity") or {}
    if identity.get("verdict") != "match":
        raise ImportFailure("validate-identity", f"{candidate_id}: PDF identity verdict must be match")
    metadata = record.get("metadata")
    if not isinstance(metadata, dict) or not metadata.get("itemType") or not metadata.get("title"):
        raise ImportFailure("validate-record", f"{candidate_id}: metadata itemType and title are required")
    pdf = record.get("pdf") or {}
    filename = str(pdf.get("filename", ""))
    if not filename.lower().endswith(".pdf") or Path(filename).name != filename:
        raise ImportFailure("validate-record", f"{candidate_id}: PDF filename must be a basename ending in .pdf")
    pdf_path = Path(str(pdf.get("local_path", ""))).expanduser().resolve()
    if not pdf_path.is_file():
        raise ImportFailure("validate-pdf", f"{candidate_id}: staged PDF is missing")
    sha256, md5, size = hash_pdf(pdf_path)
    return Candidate(
        candidate_id=candidate_id,
        pdf_path=pdf_path,
        pdf_sha256=sha256,
        pdf_md5=md5,
        pdf_size=size,
        filename=filename,
        metadata=metadata,
        allow_similar=record.get("allow_similar") is True,
    )


class AtomicJournal:
    def __init__(self, path: Path, candidate: Candidate, target: Mapping[str, Any]):
        self.path = path.resolve()
        self.data: dict[str, Any] = {
            "schema": "zotero-source-import/v2",
            "candidate_id": candidate.candidate_id,
            "pdf_sha256": candidate.pdf_sha256,
            "state": "approved-for-import",
            "target": {
                "library_type": target["library_type"],
                "library_id": str(target["library_id"]),
            },
            "zotero": {"parent_item_key": None, "attachment_key": None, "existing_item_key": None},
            "stages": {
                "deduplicate": "pending",
                "parent_create": "pending",
                "attachment_create": "pending",
                "upload_authorize": "pending",
                "storage_upload": "pending",
                "upload_register": "pending",
                "fetchback_verify": "pending",
            },
            "rollback": {
                "attachment_delete": "not-required",
                "parent_delete": "not-required",
            },
            "failure": {"operation": None, "status_code": None, "message": None},
            "updated_at": _utc_now(),
        }
        self.save()

    def update(self, **changes: Any) -> None:
        self.data.update(changes)
        self.data["updated_at"] = _utc_now()
        self.save()

    def stage(self, name: str, value: str) -> None:
        self.data["stages"][name] = value
        self.update()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=self.path.name + ".", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(self.data, stream, indent=2, sort_keys=True, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.chmod(temporary, 0o600)
            except OSError:
                pass
            for attempt in range(5):
                try:
                    os.replace(temporary, self.path)
                    break
                except PermissionError:
                    if attempt == 4:
                        raise
                    time.sleep(0.02 * (2**attempt))
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _norm_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _norm_doi(value: Any) -> str:
    doi = str(value or "").strip().lower()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
    return doi.rstrip(" .")


def _year(value: Any) -> str:
    match = re.search(r"(?:19|20)\d{2}", str(value or ""))
    return match.group(0) if match else ""


def _first_creator_surname(data: Mapping[str, Any]) -> str:
    creators = data.get("creators") or []
    if not creators:
        return ""
    creator = creators[0]
    return _norm_text(creator.get("lastName") or creator.get("name"))


def _norm_url(value: Any) -> str:
    url = str(value or "").strip().lower()
    url = re.sub(r"^https?://(?:www\.)?", "", url)
    return url.split("#", 1)[0].rstrip("/")


_TITLE_STOPWORDS = frozenset(
    "a an and as at by for from in into of on or the to with".split()
)


def _title_tokens(value: Any) -> set[str]:
    return {token for token in _norm_text(value).split() if token not in _TITLE_STOPWORDS}


def similar_titles(first: Any, second: Any) -> bool:
    """Return whether two titles name the same work, allowing for edition or version words.

    Titles match when one title's significant words all appear in the other and
    the shorter title has at least three of them, or when the two titles share at
    least four fifths of their words.
    """
    a, b = _title_tokens(first), _title_tokens(second)
    if not a or not b:
        return False
    if a == b:
        return True
    shorter, longer = sorted((a, b), key=len)
    if len(shorter) >= 3 and shorter <= longer:
        return True
    return len(a & b) / len(a | b) >= 0.8


def _search_terms(title: str) -> str:
    # We search on the longest words so that a title with an added version or
    # edition suffix still returns the library's copy.
    tokens = sorted(_title_tokens(title), key=lambda token: (-len(token), token))
    return " ".join(tokens[:4])


class ZoteroApiClient:
    def __init__(
        self,
        api_key: str,
        library_type: str,
        library_id: str,
        *,
        transport: HttpTransport | None = None,
        api_url: str = "https://api.zotero.org",
    ):
        if not api_key:
            raise ImportFailure("credentials", "Zotero API key is unavailable")
        prefix = "users" if library_type == "user" else "groups"
        self.api_url = api_url.rstrip("/")
        self.library_type = library_type
        self.library_id = library_id
        self.base = f"{self.api_url}/{prefix}/{library_id}"
        self.api_key = api_key
        self.transport = transport or UrllibTransport()

    def _headers(self, **extra: str) -> dict[str, str]:
        headers = {"Zotero-API-Key": self.api_key, "Zotero-API-Version": "3"}
        headers.update(extra)
        return headers

    def _request(
        self,
        operation: str,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes | None = None,
        allowed: tuple[int, ...] = (200,),
    ) -> HttpResponse:
        response = self.transport.request(method, url, headers=headers, body=body)
        if response.status not in allowed:
            raise ImportFailure(operation, f"Zotero returned HTTP {response.status}", response.status)
        return response

    @staticmethod
    def _json(operation: str, response: HttpResponse) -> Any:
        try:
            return json.loads(response.body)
        except (ValueError, UnicodeDecodeError):
            raise ImportFailure(operation, "Zotero returned invalid JSON", response.status) from None

    def _list_items(self, query: str) -> list[Mapping[str, Any]]:
        params = urlencode({"q": query, "qmode": "everything", "itemType": "-attachment", "limit": 100})
        response = self._request(
            "deduplicate", "GET", f"{self.base}/items?{params}", headers=self._headers()
        )
        data = self._json("deduplicate", response)
        if not isinstance(data, list):
            raise ImportFailure("deduplicate", "unexpected Zotero item-list shape")
        return data

    def verify_access(self) -> None:
        response = self._request(
            "access-preflight",
            "GET",
            f"{self.api_url}/keys/current",
            headers=self._headers(),
        )
        data = self._json("access-preflight", response)
        access = data.get("access") if isinstance(data, dict) else None
        if not isinstance(access, dict):
            raise ImportFailure("access-preflight", "API key access record is missing")
        if self.library_type == "user":
            if str(data.get("userID", "")) != self.library_id:
                raise ImportFailure(
                    "access-preflight", "API key does not belong to the target user library"
                )
            rights = access.get("user") or {}
            required = ("library", "write", "files")
        else:
            groups = access.get("groups") or {}
            rights = groups.get(self.library_id) or groups.get("all") or {}
            required = ("library", "write")
        if not all(rights.get(name) is True for name in required):
            raise ImportFailure(
                "access-preflight", "API key lacks target library write/file access"
            )

    def find_duplicate(self, metadata: Mapping[str, Any], *, allow_similar: bool = False) -> str | None:
        """Return the key of a library item that already holds this work, or None.

        A matching DOI or URL is always a duplicate. A matching or similar title is
        a duplicate unless ``allow_similar`` is set, which the author does when they
        want a different version of a work the library already holds.
        """
        doi = _norm_doi(metadata.get("DOI"))
        url = _norm_url(metadata.get("url"))
        title = str(metadata.get("title") or "")
        queries = [doi] if doi else []
        if title:
            queries.append(title)
            short = _search_terms(title)
            if short and short != _norm_text(title):
                queries.append(short)
        seen: set[str] = set()
        for query in queries:
            for item in self._list_items(query):
                key = str(item.get("key") or "")
                if not key or key in seen:
                    continue
                seen.add(key)
                data = item.get("data") or item
                if doi and _norm_doi(data.get("DOI")) == doi:
                    return key
                if url and _norm_url(data.get("url")) == url:
                    return key
                if not allow_similar and similar_titles(title, data.get("title")):
                    return key
        return None

    def _create_item(self, operation: str, data: Mapping[str, Any]) -> str:
        response = self._request(
            operation,
            "POST",
            f"{self.base}/items",
            headers=self._headers(
                **{
                    "Content-Type": "application/json",
                    "Zotero-Write-Token": uuid.uuid4().hex,
                }
            ),
            body=_canonical_json([data]),
            allowed=(200, 201),
        )
        result = self._json(operation, response)
        successful = result.get("successful") if isinstance(result, dict) else None
        if not successful:
            raise ImportFailure(operation, "Zotero did not create an item", response.status)
        first = successful[sorted(successful, key=lambda value: int(value))[0]]
        key = first.get("key")
        if not key:
            raise ImportFailure(operation, "created item has no key", response.status)
        return str(key)

    def create_parent(self, metadata: Mapping[str, Any], collection_key: str | None) -> str:
        data = dict(metadata)
        if collection_key:
            data["collections"] = [collection_key]
        return self._create_item("parent-create", data)

    def create_attachment(self, parent_key: str, filename: str) -> str:
        return self._create_item(
            "attachment-create",
            {
                "itemType": "attachment",
                "linkMode": "imported_file",
                "title": filename,
                "filename": filename,
                "contentType": "application/pdf",
                "parentItem": parent_key,
            },
        )

    def upload_pdf(
        self,
        attachment_key: str,
        filename: str,
        content: bytes,
        stage_hook: Callable[[str, str], None],
    ) -> str:
        md5 = hashlib.md5(content).hexdigest()
        auth_body = urlencode(
            {
                "md5": md5,
                "filename": filename,
                "filesize": str(len(content)),
                "mtime": str(int(time.time() * 1000)),
            }
        ).encode("ascii")
        response = self._request(
            "upload-authorize",
            "POST",
            f"{self.base}/items/{attachment_key}/file",
            headers=self._headers(
                **{
                    "If-None-Match": "*",
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            ),
            body=auth_body,
            allowed=(200,),
        )
        authorization = self._json("upload-authorize", response)
        exists_value = authorization.get("exists") if isinstance(authorization, dict) else None
        if type(exists_value) is int and exists_value == 1:
            stage_hook("upload_authorize", "exists")
            stage_hook("storage_upload", "skipped-existing")
            stage_hook("upload_register", "skipped-existing")
            return "exists"
        stage_hook("upload_authorize", "complete")
        required = {"url", "uploadKey"}
        if not isinstance(authorization, dict) or not required.issubset(authorization):
            raise ImportFailure("upload-authorize", "incomplete Zotero upload authorization")
        storage_url = str(authorization["url"])
        if not storage_url.startswith("https://"):
            raise ImportFailure("storage-upload", "refused non-HTTPS storage URL")
        prefix = authorization.get("prefix", "")
        suffix = authorization.get("suffix", "")
        prefix_bytes = prefix.encode("utf-8") if isinstance(prefix, str) else bytes(prefix)
        suffix_bytes = suffix.encode("utf-8") if isinstance(suffix, str) else bytes(suffix)
        storage = self.transport.request(
            "POST",
            storage_url,
            headers={
                "Content-Type": authorization.get(
                    "contentType", "application/x-www-form-urlencoded"
                )
            },
            body=prefix_bytes + content + suffix_bytes,
        )
        if storage.status not in (200, 201, 204):
            raise ImportFailure("storage-upload", f"storage returned HTTP {storage.status}", storage.status)
        stage_hook("storage_upload", "complete")
        register = urlencode({"upload": authorization["uploadKey"]}).encode("ascii")
        self._request(
            "upload-register",
            "POST",
            f"{self.base}/items/{attachment_key}/file",
            headers=self._headers(
                **{
                    "If-None-Match": "*",
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            ),
            body=register,
            allowed=(200, 201, 204),
        )
        stage_hook("upload_register", "complete")
        return "uploaded"

    def get_item(self, item_key: str) -> Mapping[str, Any] | None:
        response = self.transport.request(
            "GET", f"{self.base}/items/{item_key}", headers=self._headers()
        )
        if response.status == 404:
            return None
        if response.status != 200:
            raise ImportFailure("item-fetch", f"Zotero returned HTTP {response.status}", response.status)
        data = self._json("item-fetch", response)
        if not isinstance(data, dict):
            raise ImportFailure("item-fetch", "unexpected Zotero item shape")
        return data

    def verify_fetchback(
        self,
        parent_key: str,
        attachment_key: str,
        metadata: Mapping[str, Any],
        filename: str,
        content_md5: str,
    ) -> None:
        parent = self.get_item(parent_key)
        attachment = self.get_item(attachment_key)
        if not parent or not attachment:
            raise ImportFailure("fetchback-verify", "created parent or attachment is absent")
        parent_data = parent.get("data") or parent
        attachment_data = attachment.get("data") or attachment
        if _norm_text(parent_data.get("title")) != _norm_text(metadata.get("title")):
            raise ImportFailure("fetchback-verify", "parent title differs from approved metadata")
        approved_doi = _norm_doi(metadata.get("DOI"))
        if approved_doi and _norm_doi(parent_data.get("DOI")) != approved_doi:
            raise ImportFailure("fetchback-verify", "parent DOI differs from approved metadata")
        expected = {
            "parentItem": parent_key,
            "linkMode": "imported_file",
            "contentType": "application/pdf",
            "filename": filename,
        }
        for field, value in expected.items():
            if attachment_data.get(field) != value:
                raise ImportFailure("fetchback-verify", f"attachment {field} is not verified")
        remote_md5 = str(attachment_data.get("md5") or "").lower()
        if remote_md5 != content_md5:
            raise ImportFailure("fetchback-verify", "attachment file record MD5 is absent or differs")

    def item_exists(self, item_key: str) -> bool:
        return self.get_item(item_key) is not None

    def delete_item(self, item_key: str) -> None:
        item = self.get_item(item_key)
        if item is None:
            return
        version = item.get("version") or (item.get("data") or {}).get("version")
        if version is None:
            raise ImportFailure("rollback-delete", "cannot delete item without version")
        self._request(
            "rollback-delete",
            "DELETE",
            f"{self.base}/items/{item_key}",
            headers=self._headers(**{"If-Unmodified-Since-Version": str(version)}),
            allowed=(204,),
        )


def rollback(client: ZoteroClientLike, journal: AtomicJournal) -> bool:
    journal.update(state="rollback-required")
    attachment_key = journal.data["zotero"].get("attachment_key")
    parent_key = journal.data["zotero"].get("parent_item_key")
    if attachment_key:
        journal.data["rollback"]["attachment_delete"] = "pending"
        journal.save()
        try:
            client.delete_item(attachment_key)
            if client.item_exists(attachment_key):
                raise ImportFailure("rollback-attachment", "attachment still exists")
            journal.data["rollback"]["attachment_delete"] = "confirmed"
            journal.save()
        except Exception:
            journal.data["rollback"]["attachment_delete"] = "failed"
            journal.update(state="rollback-incomplete")
            return False
    if parent_key:
        journal.data["rollback"]["parent_delete"] = "pending"
        journal.save()
        try:
            client.delete_item(parent_key)
            if client.item_exists(parent_key):
                raise ImportFailure("rollback-parent", "parent still exists")
            journal.data["rollback"]["parent_delete"] = "confirmed"
            journal.save()
        except Exception:
            journal.data["rollback"]["parent_delete"] = "failed"
            journal.update(state="rollback-incomplete")
            return False
    journal.update(state="rolled-back")
    return True


def import_candidate(
    candidate: Candidate,
    target: Mapping[str, Any],
    client: ZoteroClientLike,
    journal_path: Path,
) -> dict[str, Any]:
    """Import one candidate and return its outcome; never raise for a Zotero failure."""
    journal = AtomicJournal(journal_path, candidate, target)
    try:
        duplicate = client.find_duplicate(candidate.metadata, allow_similar=candidate.allow_similar)
        if duplicate:
            journal.data["zotero"]["existing_item_key"] = duplicate
            journal.data["stages"]["deduplicate"] = "duplicate"
            journal.update(state="skipped-duplicate")
            return {
                "candidate_id": candidate.candidate_id,
                "state": "skipped-duplicate",
                "existing_item_key": duplicate,
            }
        journal.stage("deduplicate", "complete")

        parent_key = client.create_parent(candidate.metadata, target.get("collection_key"))
        journal.data["zotero"]["parent_item_key"] = parent_key
        journal.data["rollback"]["parent_delete"] = "pending"
        journal.data["stages"]["parent_create"] = "complete"
        journal.update(state="parent-created")

        attachment_key = client.create_attachment(parent_key, candidate.filename)
        journal.data["zotero"]["attachment_key"] = attachment_key
        journal.data["rollback"]["attachment_delete"] = "pending"
        journal.data["stages"]["attachment_create"] = "complete"
        journal.update(state="attachment-created")

        content = read_pdf(candidate)
        client.upload_pdf(attachment_key, candidate.filename, content, journal.stage)
        journal.update(state="storage-uploaded")

        client.verify_fetchback(
            parent_key, attachment_key, candidate.metadata, candidate.filename, candidate.pdf_md5
        )
        journal.data["stages"]["fetchback_verify"] = "complete"
        journal.data["rollback"] = {
            "attachment_delete": "not-required",
            "parent_delete": "not-required",
        }
        journal.update(state="imported-unindexed")
        return {
            "candidate_id": candidate.candidate_id,
            "state": "imported-unindexed",
            "parent_item_key": parent_key,
            "attachment_key": attachment_key,
        }
    except Exception as exc:
        failure = exc if isinstance(exc, ImportFailure) else ImportFailure(
            "internal", f"unexpected {type(exc).__name__}"
        )
        failed_stage = {
            "deduplicate": "deduplicate",
            "parent-create": "parent_create",
            "attachment-create": "attachment_create",
            "upload-authorize": "upload_authorize",
            "storage-upload": "storage_upload",
            "upload-register": "upload_register",
            "fetchback-verify": "fetchback_verify",
            "validate-pdf": "storage_upload",
        }.get(failure.operation)
        if failed_stage and journal.data["stages"].get(failed_stage) == "pending":
            journal.data["stages"][failed_stage] = "failed"
        journal.data["failure"] = {
            "operation": failure.operation,
            "status_code": failure.status_code,
            "message": failure.safe_message,
        }
        journal.update(state="failed")
        if journal.data["zotero"].get("parent_item_key"):
            rollback(client, journal)
        return {
            "candidate_id": candidate.candidate_id,
            "state": journal.data["state"],
            "operation": failure.operation,
            "message": failure.safe_message,
            "parent_item_key": journal.data["zotero"].get("parent_item_key"),
            "attachment_key": journal.data["zotero"].get("attachment_key"),
        }


def _client_for(
    target: Mapping[str, Any],
    client: ZoteroClientLike | None,
    api_key: str | None,
    transport: HttpTransport | None,
    api_url: str,
) -> ZoteroClientLike:
    if client is not None:
        return client
    return ZoteroApiClient(
        api_key or "",
        str(target["library_type"]),
        str(target["library_id"]),
        transport=transport,
        api_url=api_url,
    )


def check_batch(
    batch: Mapping[str, Any],
    *,
    api_key: str | None = None,
    client: ZoteroClientLike | None = None,
    transport: HttpTransport | None = None,
    api_url: str = "https://api.zotero.org",
) -> list[dict[str, Any]]:
    """Report, without changing the library, which candidates it already holds."""
    target, records = load_batch(batch)
    client = _client_for(target, client, api_key, transport, api_url)
    results = []
    for record in records:
        metadata = record.get("metadata") or {}
        existing = client.find_duplicate(metadata, allow_similar=record.get("allow_similar") is True)
        results.append({
            "candidate_id": record["candidate_id"],
            "state": "duplicate" if existing else "new",
            "existing_item_key": existing,
        })
    return results


def run_batch(
    batch: Mapping[str, Any],
    approved: str,
    journal_dir: Path,
    *,
    api_key: str | None = None,
    client: ZoteroClientLike | None = None,
    transport: HttpTransport | None = None,
    api_url: str = "https://api.zotero.org",
) -> list[dict[str, Any]]:
    """Import the approved candidates and return one outcome per candidate.

    Every approved candidate is validated before anything is written, so a bad
    record stops the batch with the library untouched. A candidate whose rollback
    cannot be confirmed stops the batch, and the rest are reported as not attempted.
    """
    target, records = load_batch(batch)
    selected = [validate_candidate(record) for record in select_candidates(records, approved)]
    client = _client_for(target, client, api_key, transport, api_url)
    client.verify_access()
    results: list[dict[str, Any]] = []
    for index, candidate in enumerate(selected):
        outcome = import_candidate(
            candidate, target, client, journal_dir / f"{candidate.candidate_id}.json"
        )
        results.append(outcome)
        if outcome["state"] == "rollback-incomplete":
            results.extend(
                {"candidate_id": rest.candidate_id, "state": "not-attempted"}
                for rest in selected[index + 1:]
            )
            break
    return results


def load_api_key(
    *,
    keyring_service: str | None,
    keyring_username: str | None,
    env_name: str | None,
) -> str:
    if keyring_service and keyring_username:
        try:
            import keyring  # type: ignore

            value = keyring.get_password(keyring_service, keyring_username)
            if value:
                return value
        except ImportError:
            pass
        except Exception:
            raise ImportFailure("credentials", "OS keyring lookup failed") from None
    if env_name:
        value = os.environ.get(env_name)
        if value:
            return value
    raise ImportFailure(
        "credentials",
        "Zotero API key unavailable; configure keyring or name an explicit environment variable",
    )


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise ImportFailure("load-record", f"cannot load {path.name}: {type(exc).__name__}") from None
    if not isinstance(value, dict):
        raise ImportFailure("load-record", f"{path.name} must contain one JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="report candidates the library already holds")
    mode.add_argument("--approve", help="'all' or comma-separated candidate IDs the author approved")
    parser.add_argument("--journal-dir", type=Path)
    parser.add_argument("--keyring-service")
    parser.add_argument("--keyring-username")
    parser.add_argument(
        "--api-key-env",
        help="explicit environment-variable fallback; the variable value is never output",
    )
    parser.add_argument("--api-url", default="https://api.zotero.org")
    args = parser.parse_args(argv)
    try:
        batch = _load_json(args.batch)
        if args.approve is not None and args.journal_dir is None:
            raise ImportFailure("arguments", "--journal-dir is required for import")
        api_key = load_api_key(
            keyring_service=args.keyring_service,
            keyring_username=args.keyring_username,
            env_name=args.api_key_env,
        )
        if args.check:
            results = check_batch(batch, api_key=api_key, api_url=args.api_url)
            print(json.dumps(results, indent=2, sort_keys=True))
            return 0
        results = run_batch(batch, args.approve, args.journal_dir, api_key=api_key, api_url=args.api_url)
        print(json.dumps(results, indent=2, sort_keys=True))
        settled = {"imported-unindexed", "skipped-duplicate"}
        return 0 if all(result["state"] in settled for result in results) else 1
    except ImportFailure as exc:
        print(
            json.dumps(
                {
                    "state": "failed",
                    "operation": exc.operation,
                    "status_code": exc.status_code,
                    "message": exc.safe_message,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
