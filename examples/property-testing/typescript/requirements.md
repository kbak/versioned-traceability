# Expiration

`req~expiration~1`

For nonnegative safe integer timestamps and a positive integer timeout, a
session is expired when now is at least last activity plus timeout. Equality
expires it. Shifting both timestamps equally preserves the decision when all
values and sums remain safe integers. Generators use timestamps/shifts up to
one billion and timeouts from one to one million.

Needs: impl, utest
