from __future__ import annotations

import asyncio

import pytest


def test_register_and_run_extra_plugins(registry):
    from plugins.extra_plugins import register_extra_plugins

    register_extra_plugins(registry)

    result = asyncio.run(registry.run("text_stats", {"text": "hello world"}))
    assert result.get("words") == 2
    assert result.get("chars") == 11

    result2 = asyncio.run(registry.run("reverse", {"text": "abc"}))
    assert result2.get("reversed") == "cba"
