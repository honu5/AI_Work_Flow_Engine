from pathlib import Path

from workflows.catalog.loader import load_catalog


def test_cli_catalog_usage():
    directory = Path(__file__).resolve().parents[1] / "workflows" / "catalog"
    templates = load_catalog(directory)
    names = {tpl.name for tpl in templates}
    assert "text_cleanup_pipeline" in names
    assert len(templates) >= 10
