from pathlib import Path

from workflows.catalog.loader import load_catalog


def test_catalog_files_present():
    directory = Path(__file__).resolve().parents[1] / "workflows" / "catalog"
    templates = load_catalog(directory)
    assert len(templates) >= 18
