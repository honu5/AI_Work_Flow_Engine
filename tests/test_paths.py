import pytest

from utils.paths import get_in, require_in


def test_get_in_returns_default():
    assert get_in({"a": {"b": 1}}, "a.c", default=0) == 0


def test_require_in_raises():
    with pytest.raises(KeyError):
        require_in({"a": {}}, "a.b")
