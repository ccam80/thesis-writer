#!/usr/bin/env python3
"""Import one explicitly approved source and verified PDF into Zotero.

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
    def find_duplicate(self, metadata: Mapping[str, Any]) -> str | None: ...
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


def compute_record_sha256(candidate: Mapping[str, Any]) -> str:
    """Hash the approved identity; exclude mutable workflow timestamps/state."""
    frozen = {
        "candidate_id": candidate.get("candidate_id"),
        "claim_ids": candidate.get("claim_ids"),
        "metadata": candidate.get("metadata"),
        "target": candidate.get("target"),
        "pdf_sha256": (candidate.get("pdf") or {}).get("sha256"),
        "pdf_filename": (candidate.get("pdf") or {}).get("filename"),
        "pdf_identity": candidate.get("pdf_identity"),
    }
    return hashlib.sha256(_canonical_json(frozen)).hexdigest()


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


def read_frozen_pdf(candidate: "FrozenCandidate") -> bytes:
    """Read once for upload and close the validation-to-upload race."""
    try:
        content = candidate.pdf_path.read_bytes()
    except OSError as exc:
        raise ImportFailure("validate-pdf", f"cannot reread staged PDF: {type(exc).__name__}") from None
    if content[:5] != b"%PDF-" or len(content) != candidate.pdf_size:
        raise ImportFailure("validate-pdf", "staged PDF changed before upload")
    if hashlib.sha256(content).hexdigest() != candidate.pdf_sha256:
        raise ImportFailure("validate-pdf", "staged PDF changed before upload")
    return content


_APPROVAL_RE = re.compile(r"\s*Approve import:\s*([A-Za-z0-9_-]+(?:\s*,\s*[A-Za-z0-9_-]+)*)\s*\Z")


@dataclass(frozen=True)
class FrozenCandidate:
    candidate_id: str
    record_sha256: str
    pdf_path: Path
    pdf_sha256: str
    pdf_md5: str
    pdf_size: int
    filename: str
    metadata: Mapping[str, Any]
    target: Mapping[str, Any]


def validate_and_freeze(
    candidate: Mapping[str, Any], approval: Mapping[str, Any]
) -> FrozenCandidate:
    if candidate.get("schema") != "zotero-source-candidate/v1":
        raise ImportFailure("validate-record", "unsupported candidate schema")
    if approval.get("schema") != "zotero-source-approval/v1":
        raise ImportFailure("validate-approval", "unsupported approval schema")
    candidate_id = candidate.get("candidate_id")
    if not isinstance(candidate_id, str) or not candidate_id:
        raise ImportFailure("validate-record", "candidate_id is required")
    approved_ids = approval.get("approved_candidate_ids")
    if not isinstance(approved_ids, list) or not all(isinstance(v, str) for v in approved_ids):
        raise ImportFailure("validate-approval", "approved_candidate_ids must be a string list")
    approval_match = _APPROVAL_RE.fullmatch(str(approval.get("approval_text", "")))
    if not approval_match:
        raise ImportFailure("validate-approval", "approval_text must name exact candidate IDs")
    text_ids = [value.strip() for value in approval_match.group(1).split(",")]
    if len(set(approved_ids)) != len(approved_ids) or set(text_ids) != set(approved_ids):
        raise ImportFailure("validate-approval", "approval text and approved ID list differ")
    if candidate_id not in approved_ids:
        raise ImportFailure("validate-approval", f"candidate {candidate_id} was not approved")
    identity = candidate.get("pdf_identity") or {}
    if identity.get("verdict") != "match":
        raise ImportFailure("validate-identity", "PDF identity verdict must be match")

    pdf = candidate.get("pdf") or {}
    pdf_path = Path(str(pdf.get("local_path", ""))).expanduser().resolve()
    if not pdf_path.is_file():
        raise ImportFailure("validate-pdf", "staged PDF is missing")
    actual_sha256, actual_md5, actual_size = hash_pdf(pdf_path)
    if actual_sha256 != str(pdf.get("sha256", "")).lower():
        raise ImportFailure("validate-pdf", "staged PDF SHA-256 changed")
    if actual_size != pdf.get("byte_count"):
        raise ImportFailure("validate-pdf", "staged PDF byte count changed")

    actual_record_hash = compute_record_sha256(candidate)
    if actual_record_hash != str(candidate.get("record_sha256", "")).lower():
        raise ImportFailure("validate-record", "candidate record hash is absent or changed")
    approved_hashes = approval.get("approved_record_sha256") or {}
    if approved_hashes.get(candidate_id) != actual_record_hash:
        raise ImportFailure("validate-approval", "approval does not freeze this candidate record")
    metadata = candidate.get("metadata")
    target = candidate.get("target")
    if not isinstance(metadata, dict) or not metadata.get("itemType") or not metadata.get("title"):
        raise ImportFailure("validate-record", "metadata itemType and title are required")
    if not isinstance(target, dict) or target.get("library_type") not in {"user", "group"}:
        raise ImportFailure("validate-record", "target library_type is invalid")
    if not str(target.get("library_id", "")):
        raise ImportFailure("validate-record", "target library_id is required")
    filename = str(pdf.get("filename", ""))
    if not filename.lower().endswith(".pdf") or Path(filename).name != filename:
        raise ImportFailure("validate-record", "PDF filename must be a basename ending in .pdf")
    return FrozenCandidate(
        candidate_id=candidate_id,
        record_sha256=actual_record_hash,
        pdf_path=pdf_path,
        pdf_sha256=actual_sha256,
        pdf_md5=actual_md5,
        pdf_size=actual_size,
        filename=filename,
        metadata=metadata,
        target=target,
    )


class AtomicJournal:
    def __init__(self, path: Path, candidate: FrozenCandidate):
        self.path = path.resolve()
        self.data: dict[str, Any] = {
            "schema": "zotero-source-import/v1",
            "candidate_id": candidate.candidate_id,
            "approved_record_sha256": candidate.record_sha256,
            "state": "approved-for-import",
            "target": {
                "library_type": candidate.target["library_type"],
                "library_id": str(candidate.target["library_id"]),
            },
            "zotero": {"parent_item_key": None, "attachment_key": None},
            "stages": {
                "access_preflight": "pending",
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

    def find_duplicate(self, metadata: Mapping[str, Any]) -> str | None:
        doi = _norm_doi(metadata.get("DOI"))
        title = _norm_text(metadata.get("title"))
        creator = _first_creator_surname(metadata)
        year = _year(metadata.get("date"))
        queries = [doi] if doi else []
        if title:
            queries.append(str(metadata.get("title")))
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
                same_title = title and _norm_text(data.get("title")) == title
                same_creator = creator and _first_creator_surname(data) == creator
                same_year = year and _year(data.get("date")) == year
                if same_title and same_creator and same_year:
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


def run_import(
    candidate: Mapping[str, Any],
    approval: Mapping[str, Any],
    journal_path: Path,
    *,
    api_key: str | None = None,
    client: ZoteroClientLike | None = None,
    transport: HttpTransport | None = None,
    api_url: str = "https://api.zotero.org",
) -> Mapping[str, Any]:
    frozen = validate_and_freeze(candidate, approval)
    journal = AtomicJournal(journal_path, frozen)
    if client is None:
        client = ZoteroApiClient(
            api_key or "",
            str(frozen.target["library_type"]),
            str(frozen.target["library_id"]),
            transport=transport,
            api_url=api_url,
        )
    try:
        client.verify_access()
        journal.stage("access_preflight", "complete")
        duplicate = client.find_duplicate(frozen.metadata)
        if duplicate:
            raise DuplicateCandidate(duplicate)
        journal.stage("deduplicate", "complete")

        parent_key = client.create_parent(
            frozen.metadata, frozen.target.get("collection_key")
        )
        journal.data["zotero"]["parent_item_key"] = parent_key
        journal.data["rollback"]["parent_delete"] = "pending"
        journal.data["stages"]["parent_create"] = "complete"
        journal.update(state="parent-created")

        attachment_key = client.create_attachment(parent_key, frozen.filename)
        journal.data["zotero"]["attachment_key"] = attachment_key
        journal.data["rollback"]["attachment_delete"] = "pending"
        journal.data["stages"]["attachment_create"] = "complete"
        journal.update(state="attachment-created")

        content = read_frozen_pdf(frozen)
        client.upload_pdf(attachment_key, frozen.filename, content, journal.stage)
        journal.update(state="storage-uploaded")

        client.verify_fetchback(
            parent_key, attachment_key, frozen.metadata, frozen.filename, frozen.pdf_md5
        )
        journal.data["stages"]["fetchback_verify"] = "complete"
        journal.data["rollback"] = {
            "attachment_delete": "not-required",
            "parent_delete": "not-required",
        }
        journal.update(state="imported-unindexed")
        return {
            "candidate_id": frozen.candidate_id,
            "state": "imported-unindexed",
            "parent_item_key": parent_key,
            "attachment_key": attachment_key,
        }
    except Exception as exc:
        failure = exc if isinstance(exc, ImportFailure) else ImportFailure(
            "internal", f"unexpected {type(exc).__name__}"
        )
        failed_stage = {
            "access-preflight": "access_preflight",
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
        raise failure


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
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--journal", type=Path)
    parser.add_argument("--dry-validate", action="store_true")
    parser.add_argument("--compute-record-hash", action="store_true")
    parser.add_argument("--keyring-service")
    parser.add_argument("--keyring-username")
    parser.add_argument(
        "--api-key-env",
        help="explicit environment-variable fallback; the variable value is never output",
    )
    parser.add_argument("--api-url", default="https://api.zotero.org")
    args = parser.parse_args(argv)
    try:
        candidate = _load_json(args.candidate)
        if args.compute_record_hash:
            print(compute_record_sha256(candidate))
            return 0
        if args.approval is None:
            raise ImportFailure("arguments", "--approval is required unless computing a record hash")
        approval = _load_json(args.approval)
        frozen = validate_and_freeze(candidate, approval)
        if args.dry_validate:
            print(json.dumps({"candidate_id": frozen.candidate_id, "state": "approved-for-import"}))
            return 0
        if args.journal is None:
            raise ImportFailure("arguments", "--journal is required for import")
        api_key = load_api_key(
            keyring_service=args.keyring_service,
            keyring_username=args.keyring_username,
            env_name=args.api_key_env,
        )
        result = run_import(
            candidate,
            approval,
            args.journal,
            api_key=api_key,
            api_url=args.api_url,
        )
        print(json.dumps(result, sort_keys=True))
        return 0
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
