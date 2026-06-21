from pathlib import Path

from services.source_lookup_service import source_by_id


def test_source_by_id_returns_matching_source_chunk():
    chunks = [
        {"source_id": "S1", "text": "first"},
        {"source_id": "S2", "text": "second"},
    ]

    assert source_by_id(chunks, "S2") == {"source_id": "S2", "text": "second"}


def test_source_by_id_returns_empty_dict_for_missing_source():
    chunks = [{"source_id": "S1", "text": "first"}]

    assert source_by_id(chunks, "S9") == {}


def test_source_by_id_handles_empty_inputs():
    assert source_by_id([], "S1") == {}
    assert source_by_id(None, "S1") == {}
    assert source_by_id([{"source_id": "S1"}], None) == {}


def test_compliance_studio_uses_extracted_source_lookup_service():
    text = Path("modules/compliance_studio.py").read_text(encoding="utf-8")

    assert "from services.source_lookup_service import source_by_id" in text
    assert "def _source_by_id" not in text
    assert "_source_by_id(" not in text
