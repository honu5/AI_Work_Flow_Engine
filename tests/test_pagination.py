from utils.pagination import paginate


def test_paginate_slices():
    page = paginate(list(range(100)), offset=10, limit=5)
    assert page.items == [10, 11, 12, 13, 14]
    assert page.total == 100
