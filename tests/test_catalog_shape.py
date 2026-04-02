from pathlib import Path

from workflows.catalog.loader import load_catalog


def test_catalog_template_shape():
    directory = Path(__file__).resolve().parents[1] / "workflows" / "catalog"
    templates = load_catalog(directory)
    sample = templates[0]
    assert sample.nodes
