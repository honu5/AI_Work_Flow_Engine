import pytest

from plugins.base import Plugin
from plugins.validation import validate_input, validate_output


class SamplePlugin(Plugin):
    name = "sample"
    version = "1.0.0"
    description = "sample"

    async def run(self, payload):
        return payload


def test_validation_passthrough():
    plugin = SamplePlugin()
    payload = {"x": 1}
    assert validate_input(plugin, payload) == payload
    assert validate_output(plugin, payload) == payload
