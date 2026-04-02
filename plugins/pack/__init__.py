from plugins.pack.text import register_text_plugins
from plugins.pack.math import register_math_plugins
from plugins.pack.json_ops import register_json_plugins
from plugins.pack.time_ops import register_time_plugins
from plugins.pack.data_ops import register_data_plugins
from plugins.pack.logic import register_logic_plugins
from plugins.pack.collections import register_collection_plugins
from plugins.pack.formatting import register_formatting_plugins
from plugins.pack.routing import register_routing_plugins
from plugins.pack.validation_ops import register_validation_plugins
from plugins.pack.analysis import register_analysis_plugins
from plugins.pack.aggregate import register_aggregate_plugins
from plugins.pack.transform import register_transform_plugins
from plugins.pack.statistics import register_statistics_plugins
from plugins.pack.encoding import register_encoding_plugins
from plugins.pack.strings import register_string_plugins
from plugins.pack.records import register_record_plugins
from plugins.pack.datetime_parse import register_datetime_parse_plugins


def register_plugin_pack(registry) -> None:
    register_text_plugins(registry)
    register_math_plugins(registry)
    register_json_plugins(registry)
    register_time_plugins(registry)
    register_data_plugins(registry)
    register_logic_plugins(registry)
    register_collection_plugins(registry)
    register_formatting_plugins(registry)
    register_routing_plugins(registry)
    register_validation_plugins(registry)
    register_analysis_plugins(registry)
    register_transform_plugins(registry)
    register_aggregate_plugins(registry)
    register_statistics_plugins(registry)
    register_encoding_plugins(registry)
    register_string_plugins(registry)
    register_record_plugins(registry)
    register_datetime_parse_plugins(registry)
