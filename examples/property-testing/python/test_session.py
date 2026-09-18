import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from session import expired


@pytest.mark.oft_id("utest~expiration-postcondition~1")
@settings(database=None, derandomize=True, max_examples=100)
@example(last=0, now=1, timeout=1)
@example(last=0, now=2, timeout=1)
@given(
    last=st.integers(-(10**9), 10**9),
    now=st.integers(-(10**9), 10**9),
    timeout=st.integers(1, 10**6),
)
def test_expiration_postcondition(last, now, timeout):
    # [utest~expiration-postcondition~1->req~expiration~1]
    assert expired(last, now, timeout) == (now - last >= timeout)


@pytest.mark.oft_id("utest~expiration-boundary~1")
@settings(database=None, derandomize=True, max_examples=100)
@given(last=st.integers(0, 10**9), timeout=st.integers(1, 10**6))
def test_expiration_boundary(last, timeout):
    # [utest~expiration-boundary~1->req~expiration~1]
    assert not expired(last, last + timeout - 1, timeout)
    assert expired(last, last + timeout, timeout)


@pytest.mark.oft_id("utest~expiration-shift~1")
@settings(database=None, derandomize=True, max_examples=100)
@given(
    last=st.integers(0, 10**9),
    now=st.integers(0, 10**9),
    timeout=st.integers(1, 10**6),
    shift=st.integers(0, 10**9),
)
def test_translation_preserves_expiration(last, now, timeout, shift):
    # [utest~expiration-shift~1->req~expiration~1]
    assert expired(last, now, timeout) == expired(last + shift, now + shift, timeout)
