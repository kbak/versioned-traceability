# Independently evolving retry promises

## Exponential growth
`req~retry-growth~1`

For a nonnegative attempt number n, exponential growth produces 2 raised to n.
This value is independent of the cap policy.

Needs: impl, utest

## Maximum retry delay
`req~retry-cap~1`

Capping a nonnegative delay returns the smaller of the delay and 8 seconds.

Needs: impl, utest
