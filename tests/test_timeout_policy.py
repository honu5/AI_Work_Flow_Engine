from execution.policies import TimeoutPolicy


def test_timeout_policy_parse():
    node = {"timeout_seconds": 1.5}
    policy = TimeoutPolicy.from_node(node)
    assert policy.timeout_seconds == 1.5
