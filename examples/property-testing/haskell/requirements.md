# Expiration

`req~expiration~1`

For integer timestamps and a positive integer timeout, a session is expired
when now is at least last activity plus timeout. Equality expires it. Shifting
both timestamps equally preserves the decision.

**Domain:** `last` and `now` are integer timestamps in the same unit; `timeout`
is a positive integer. `result` is the Boolean returned by `expired last now timeout`.

**Assumptions:** mathematical integer arithmetic without overflow, represented
by Haskell `Integer`. This function compares supplied timestamps; it does not read a clock.

**Logical statement (postcondition):** for every input in the domain, on return,
`result` is true if and only if `now >= last + timeout`.

**Test search:** the postcondition test generates signed timestamps with magnitude
up to one billion and timeouts from one to one million, plus explicit examples
at and after expiration. Boundary and translation tests use nonnegative timestamps
and shifts up to one billion. These ranges bound the search, not the requirement.

Needs: impl, utest
