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


def candidate(tmp_path: Path, candidate_id: str, title: str, verdict: str = "match") -> dict:
    pdf = tmp_path / f"{candidate_id}.pdf"
    pdf.write_bytes(b"%PDF-1.7\n" + f"{candidate_id} payload\n".encode() * 200)
    return {
        "candidate_id": candidate_id,
        "metadata": {
            "itemType": "journalArticle",
            "title": title,
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "Author"}],
            "date": "2025",
        },
        "pdf": {"local_path": str(pdf), "filename": f"{candidate_id}.pdf"},
        "pdf_identity": {"verdict": verdict},
    }


def batch(*candidates: dict) -> dict:
    return {
        "schema": "zotero-source-batch/v2",
        "target": {"library_type": "user", "library_id": "123"},
        "candidates": list(candidates),
    }


class FakeClient:
    """Records every call; creates keys from the candidate title."""

    def __init__(self, *, duplicates=(), fail_verify=(), undeletable=()):
        self.duplicates = set(duplicates)
        self.fail_verify = set(fail_verify)
        self.undeletable = set(undeletable)
        self.calls: list[str] = []
        self.existing: set[str] = set()

    def verify_access(self):
        self.calls.append("access")

    def find_duplicate(self, metadata, *, allow_similar=False):
        self.calls.append(f"dedupe:{metadata['title']}")
        return "EXISTING" if metadata["title"] in self.duplicates else None

    def create_parent(self, metadata, collection_key):
        key = f"P-{metadata['title']}"
        self.calls.append(f"parent:{key}")
        self.existing.add(key)
        return key

    def create_attachment(self, parent_key, filename):
        key = f"A-{parent_key[2:]}"
        self.calls.append(f"attachment:{key}")
        self.existing.add(key)
        return key

    def upload_pdf(self, attachment_key, filename, content, stage_hook):
        self.calls.append(f"upload:{attachment_key}")
        stage_hook("upload_authorize", "complete")
        stage_hook("storage_upload", "complete")
        stage_hook("upload_register", "complete")
        return "uploaded"

    def verify_fetchback(self, parent_key, *args):
        self.calls.append(f"verify:{parent_key}")
        if parent_key[2:] in self.fail_verify:
            raise RuntimeError("unsafe remote detail")

    def delete_item(self, key):
        self.calls.append(f"delete:{key}")
        if key not in self.undeletable:
            self.existing.discard(key)

    def item_exists(self, key):
        return key in self.existing

    def mutations(self) -> list[str]:
        return [call for call in self.calls if call.split(":")[0] in {"parent", "attachment", "upload", "delete"}]


def test_approved_candidates_import_and_each_gets_a_journal(importer, tmp_path: Path) -> None:
    records = batch(candidate(tmp_path, "SRC-0001", "First Source"), candidate(tmp_path, "SRC-0002", "Second Source"))
    client = FakeClient()
    results = importer.run_batch(records, "all", tmp_path / "journals", client=client)

    assert [r["state"] for r in results] == ["imported-unindexed", "imported-unindexed"]
    assert results[0]["parent_item_key"] == "P-First Source"
    for candidate_id in ("SRC-0001", "SRC-0002"):
        saved = json.loads((tmp_path / "journals" / f"{candidate_id}.json").read_text(encoding="utf-8"))
        assert saved["state"] == "imported-unindexed"
    assert client.calls[0] == "access"


def test_only_the_named_candidates_are_imported(importer, tmp_path: Path) -> None:
    records = batch(candidate(tmp_path, "SRC-0001", "First Source"), candidate(tmp_path, "SRC-0002", "Second Source"))
    client = FakeClient()
    results = importer.run_batch(records, "SRC-0002", tmp_path / "journals", client=client)

    assert [r["candidate_id"] for r in results] == ["SRC-0002"]
    assert not any("First Source" in call for call in client.calls)


@pytest.mark.parametrize("approval", ["SRC-0001, SRC-0009", "", " , "])
def test_an_approval_naming_nothing_known_changes_nothing(importer, tmp_path: Path, approval: str) -> None:
    records = batch(candidate(tmp_path, "SRC-0001", "First Source"))
    client = FakeClient()
    with pytest.raises(importer.ImportFailure):
        importer.run_batch(records, approval, tmp_path / "journals", client=client)
    assert client.calls == []


@pytest.mark.parametrize("verdict", ["weak", "mismatch", "unreadable"])
def test_a_pdf_without_a_matching_identity_stops_the_batch_before_any_write(importer, tmp_path: Path, verdict: str) -> None:
    records = batch(
        candidate(tmp_path, "SRC-0001", "First Source"),
        candidate(tmp_path, "SRC-0002", "Second Source", verdict=verdict),
    )
    client = FakeClient()
    with pytest.raises(importer.ImportFailure, match="identity"):
        importer.run_batch(records, "all", tmp_path / "journals", client=client)
    assert client.calls == []


def test_a_non_pdf_stops_the_batch_before_any_write(importer, tmp_path: Path) -> None:
    record = candidate(tmp_path, "SRC-0001", "First Source")
    Path(record["pdf"]["local_path"]).write_bytes(b"<html>login page</html>" * 200)
    client = FakeClient()
    with pytest.raises(importer.ImportFailure, match="PDF"):
        importer.run_batch(batch(record), "all", tmp_path / "journals", client=client)
    assert client.calls == []


def test_a_duplicate_is_skipped_and_the_batch_continues(importer, tmp_path: Path) -> None:
    records = batch(candidate(tmp_path, "SRC-0001", "Held Already"), candidate(tmp_path, "SRC-0002", "New Source"))
    client = FakeClient(duplicates={"Held Already"})
    results = importer.run_batch(records, "all", tmp_path / "journals", client=client)

    assert results[0] == {"candidate_id": "SRC-0001", "state": "skipped-duplicate", "existing_item_key": "EXISTING"}
    assert results[1]["state"] == "imported-unindexed"
    assert not any("Held Already" in call for call in client.mutations())


def test_a_failed_candidate_rolls_back_attachment_first_and_the_batch_continues(importer, tmp_path: Path) -> None:
    records = batch(candidate(tmp_path, "SRC-0001", "Broken"), candidate(tmp_path, "SRC-0002", "Fine"))
    client = FakeClient(fail_verify={"Broken"})
    results = importer.run_batch(records, "all", tmp_path / "journals", client=client)

    assert results[0]["state"] == "rolled-back"
    assert results[0]["message"] == "unexpected RuntimeError"
    deletes = [call for call in client.calls if call.startswith("delete:")]
    assert deletes == ["delete:A-Broken", "delete:P-Broken"]
    assert results[1]["state"] == "imported-unindexed"


def test_an_unconfirmed_rollback_stops_the_batch(importer, tmp_path: Path) -> None:
    records = batch(candidate(tmp_path, "SRC-0001", "Broken"), candidate(tmp_path, "SRC-0002", "Fine"))
    client = FakeClient(fail_verify={"Broken"}, undeletable={"A-Broken"})
    results = importer.run_batch(records, "all", tmp_path / "journals", client=client)

    assert results[0]["state"] == "rollback-incomplete"
    assert results[0]["attachment_key"] == "A-Broken"
    assert results[1] == {"candidate_id": "SRC-0002", "state": "not-attempted"}
    assert not any("Fine" in call for call in client.calls)


def test_check_reports_duplicates_without_writing(importer, tmp_path: Path) -> None:
    records = batch(candidate(tmp_path, "SRC-0001", "Held Already"), candidate(tmp_path, "SRC-0002", "New Source"))
    client = FakeClient(duplicates={"Held Already"})
    results = importer.check_batch(records, client=client)

    assert [(r["candidate_id"], r["state"]) for r in results] == [("SRC-0001", "duplicate"), ("SRC-0002", "new")]
    assert client.mutations() == []


@pytest.mark.parametrize(
    "first,second,expected",
    [
        ("NVIDIA H100 Tensor Core GPU Architecture", "NVIDIA H100 Tensor Core GPU Architecture Whitepaper v1.04", True),
        ("NVIDIA Turing GPU Architecture", "NVIDIA Turing GPU Architecture", True),
        ("NVIDIA H100 Tensor Core GPU Architecture", "NVIDIA A100 Tensor Core GPU Architecture", False),
        ("Deep learning", "Deep learning for control", False),
    ],
)
def test_similar_titles_catch_versions_but_not_neighbouring_products(importer, first, second, expected) -> None:
    assert importer.similar_titles(first, second) is expected


class QueueTransport:
    def __init__(self, importer, responses):
        self.importer = importer
        self.responses = list(responses)
        self.urls: list[str] = []

    def request(self, method, url, **kwargs):
        self.urls.append(url)
        return self.responses.pop(0) if self.responses else self.importer.HttpResponse(200, {}, b"[]")


def response(importer, status: int, payload: object):
    return importer.HttpResponse(status, {}, json.dumps(payload).encode())


def library_item(key: str, **data) -> dict:
    return {"key": key, "data": data}


def test_find_duplicate_treats_a_new_version_as_held_unless_the_author_allows_it(importer) -> None:
    held = [library_item("V8ZE9PWB", title="NVIDIA H100 Tensor Core GPU Architecture")]
    metadata = {"title": "NVIDIA H100 Tensor Core GPU Architecture Whitepaper v1.04"}

    transport = QueueTransport(importer, [response(importer, 200, held)])
    client = importer.ZoteroApiClient("secret", "user", "123", transport=transport)
    assert client.find_duplicate(metadata) == "V8ZE9PWB"

    transport = QueueTransport(importer, [response(importer, 200, held)] * 2)
    client = importer.ZoteroApiClient("secret", "user", "123", transport=transport)
    assert client.find_duplicate(metadata, allow_similar=True) is None


def test_find_duplicate_always_matches_a_doi_or_url(importer) -> None:
    held = [library_item("KEY1", title="Something else", DOI="10.1000/X", url="https://www.example.org/doc/")]
    for metadata in (
        {"title": "Paper", "DOI": "https://doi.org/10.1000/x"},
        {"title": "Paper", "url": "http://example.org/doc"},
    ):
        transport = QueueTransport(importer, [response(importer, 200, held)] * 3)
        client = importer.ZoteroApiClient("secret", "user", "123", transport=transport)
        assert client.find_duplicate(metadata, allow_similar=True) == "KEY1"


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


def test_import_without_a_journal_directory_is_refused(importer, tmp_path: Path, capsys) -> None:
    path = tmp_path / "batch.json"
    path.write_text(json.dumps(batch(candidate(tmp_path, "SRC-0001", "First Source"))), encoding="utf-8")
    assert importer.main(["--batch", str(path), "--approve", "all"]) == 1
    assert "--journal-dir is required" in capsys.readouterr().err
