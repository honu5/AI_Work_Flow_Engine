from execution.policies import CachePolicy


def test_cache_policy_key_fields():
    node = {"cache": {"key_fields": ["input.a", "node.id"], "ttl_seconds": 10}}
    policy = CachePolicy.from_node(node)
    assert policy.key_fields == ["input.a", "node.id"]
    assert policy.ttl_seconds == 10
