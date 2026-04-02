import pytest

from plugins.semver import satisfies


def test_semver_exact_match():
    assert satisfies("1.2.3", "1.2.3") is True


def test_semver_caret():
    assert satisfies("1.4.0", "^1.2.0") is True
    assert satisfies("2.0.0", "^1.2.0") is False


def test_semver_tilde():
    assert satisfies("1.2.5", "~1.2.0") is True
    assert satisfies("1.3.0", "~1.2.0") is False


def test_semver_comparators():
    assert satisfies("1.2.3", ">=1.0.0") is True
    assert satisfies("1.2.3", "<2.0.0") is True
    assert satisfies("1.2.3", ">1.2.3") is False
