from storage.repository import Repository


def test_repository_list_workflows_filter(repository: Repository):
    repository.create_workflow("wf-1", "alpha", {"nodes": []})
    repository.create_workflow("wf-2", "beta", {"nodes": []})

    results = repository.list_workflows(name_contains="alpha")
    assert len(results) == 1
    assert results[0]["name"] == "alpha"
