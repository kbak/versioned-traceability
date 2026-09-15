import pytest
from session import expired


# [utest~expiration-boundary~1->req~session-expiration~1]
@pytest.mark.oft_id("utest~expiration-boundary~1")
@pytest.mark.parametrize("seconds, expected", [(1799, False), (1800, True), (1801, True)])
def test_expiration_boundary(seconds, expected):
    assert expired(seconds) is expected


def test_smoke():
    assert callable(expired)
