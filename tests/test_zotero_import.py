from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "skills" / "zotero-source-acquisition" / "scripts" / "zotero_import.py"


def load_importer():
    spec = importlib.util.spec_from_file_location("zotero_import", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def importer():
    return load_importer()


def approved_records(importer, tmp_path: Path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.7\n" + b"verified-payload\n" * 160)
    sha256, _, size = importer.hash_pdf(pdf)
    candidate = {
        "schema": "zotero-source-candidate/v1",
        "candidate_id": "SRC-0001",
        "claim_ids": ["C03-S02-P01-OP01"],
        "state": "candidate",
        "metadata": {
            "itemType": "journalArticle",
            "title": "A Verified Source",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "Author"}],
            "date": "2025",
            "DOI": "10.1000/example",
            "url": "https://publisher.example/article",
        },
        "target": {"library_type": "user", "library_id": "123"},
        "pdf": {
            "local_path": str(pdf),
            "filename": "verified-source.pdf",
            "sha256": sha256,
            "byte_count": size,
        },
        "pdf_identity": {"verdict": "match", "signals": {"doi": "match"}},
    }
    candidate["record_sha256"] = importer.compute_record_sha256(candidate)
    approval = {
        "schema": "zotero-source-approval/v1",
        "approved_candidate_ids": ["SRC-0001"],
        "approved_record_sha256": {"SRC-0001": candidate["record_sha256"]},
        "approval_text": "Approve import: SRC-0001",
    }
    return candidate, approval


class FakeClient:
    def __init__(self, *, fail_verify: bool = False):
        self.fail_verify = fail_verify
        self.calls: list[str] = []
        self.existing = {"PARENT01", "ATTACH01"}

    def verify_access(self):
        self.calls.append("access")

    def find_duplicate(self, metadata):
        self.calls.append("dedupe")
        return None

    def create_parent(self, metadata, collection_key):
        self.calls.append("parent")
        return "PARENT01"

    def create_attachment(self, parent_key, filename):
        self.calls.append("attachment")
        return "ATTACH01"

    def upload_pdf(self, attachment_key, filename, content, stage_hook):
        self.calls.append("upload")
        stage_hook("upload_authorize", "complete")
        stage_hook("storage_upload", "complete")
        stage_hook("upload_register", "complete")
        return "uploaded"

    def verify_fetchback(self, *args):
        self.calls.append("verify")
        if self.fail_verify:
            raise RuntimeError("unsafe remote detail")

    def delete_item(self, key):
        self.calls.append(f"delete:{key}")
        self.existing.discard(key)

    def item_exists(self, key):
        return key in self.existing


def test_approved_import_succeeds_and_records_keys(importer, tmp_path: Path) -> None:
    candidate, approval = approved_records(importer, tmp_path)
    client = FakeClient()
    journal = tmp_path / "journal.json"
    result = importer.run_import(candidate, approval, journal, client=client)
    assert result == {
        "candidate_id": "SRC-0001",
        "state": "imported-unindexed",
        "parent_item_key": "PARENT01",
        "attachment_key": "ATTACH01",
    }
    saved = json.loads(journal.read_text(encoding="utf-8"))
    assert saved["state"] == "imported-unindexed"
    assert saved["stages"]["access_preflight"] == "complete"
    assert client.calls[:4] == ["access", "dedupe", "parent", "attachment"]


def test_required_stage_failure_rolls_back_attachment_then_parent(importer, tmp_path: Path) -> None:
    candidate, approval = approved_records(importer, tmp_path)
    client = FakeClient(fail_verify=True)
    journal = tmp_path / "journal.json"
    with pytest.raises(importer.ImportFailure) as caught:
        importer.run_import(candidate, approval, journal, client=client)
    assert caught.value.operation == "internal"
    assert client.calls[-2:] == ["delete:ATTACH01", "delete:PARENT01"]
    saved = json.loads(journal.read_text(encoding="utf-8"))
    assert saved["state"] == "rolled-back"
    assert saved["failure"]["message"] == "unexpected RuntimeError"


def test_changed_pdf_or_nonexact_approval_is_rejected_before_mutation(importer, tmp_path: Path) -> None:
    candidate, approval = approved_records(importer, tmp_path)
    approval["approval_text"] = "yes, import it"
    with pytest.raises(importer.ImportFailure, match="exact candidate IDs"):
        importer.validate_and_freeze(candidate, approval)


class QueueTransport:
    def __init__(self, importer, responses):
        self.importer = importer
        self.responses = list(responses)

    def request(self, *args, **kwargs):
        return self.responses.pop(0)


def response(importer, status: int, payload: object):
    return importer.HttpResponse(status, {}, json.dumps(payload).encode())


def test_zotero_upload_exists_is_a_200_payload_not_412(importer) -> None:
    transport = QueueTransport(importer, [response(importer, 200, {"exists": 1})])
    client = importer.ZoteroApiClient("secret", "user", "123", transport=transport)
    stages = {}
    assert client.upload_pdf("ATTACH01", "x.pdf", b"%PDF-data", stages.__setitem__) == "exists"
    assert stages == {
        "upload_authorize": "exists",
        "storage_upload": "skipped-existing",
        "upload_register": "skipped-existing",
    }

    conflict = QueueTransport(importer, [response(importer, 412, {})])
    client = importer.ZoteroApiClient("secret", "user", "123", transport=conflict)
    with pytest.raises(importer.ImportFailure) as caught:
        client.upload_pdf("ATTACH01", "x.pdf", b"%PDF-data", lambda *_: None)
    assert caught.value.status_code == 412


@pytest.mark.parametrize("malformed_exists", [True, "1", 2])
def test_zotero_upload_rejects_malformed_truthy_exists_payload(importer, malformed_exists) -> None:
    transport = QueueTransport(importer, [response(importer, 200, {"exists": malformed_exists})])
    client = importer.ZoteroApiClient("secret", "user", "123", transport=transport)
    with pytest.raises(importer.ImportFailure, match="incomplete Zotero upload authorization"):
        client.upload_pdf("ATTACH01", "x.pdf", b"%PDF-data", lambda *_: None)


def test_access_preflight_requires_user_write_and_file_rights(importer) -> None:
    allowed = QueueTransport(
        importer,
        [response(importer, 200, {"userID": 123, "access": {"user": {"library": True, "write": True, "files": True}}})],
    )
    importer.ZoteroApiClient("secret", "user", "123", transport=allowed).verify_access()

    denied = QueueTransport(
        importer,
        [response(importer, 200, {"userID": 123, "access": {"user": {"library": True, "write": True, "files": False}}})],
    )
    with pytest.raises(importer.ImportFailure, match="write/file"):
        importer.ZoteroApiClient("secret", "user", "123", transport=denied).verify_access()
