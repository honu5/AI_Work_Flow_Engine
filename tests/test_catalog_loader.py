from pathlib import Path

from workflows.catalog.loader import load_catalog


def test_catalog_loader(tmp_path: Path):
    sample = tmp_path / "sample.json"
    sample.write_text(
        "[{\"name\": \"test\", \"nodes\": [{\"id\": \"n1\", \"plugin\": \"echo\"}]}]",
        encoding="utf-8",
    )
    templates = load_catalog(tmp_path)
    assert templates[0].name == "test"
