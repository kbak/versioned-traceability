# Expiration

`req~expiration~1`

For integer timestamps and a positive integer timeout, a session is expired
when now is at least last activity plus timeout. Equality expires it. Shifting
both timestamps equally preserves the decision. Tests use arbitrary-precision
Integer values, nonnegative timestamps/shifts up to one billion, and positive
timeouts up to one million.

Needs: impl, utest
