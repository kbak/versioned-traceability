# Expiration

`req~expiration~1`

For nonnegative safe integer timestamps and a positive integer timeout, a
session is expired when now is at least last activity plus timeout. Equality
expires it. Shifting both timestamps equally preserves the decision when all
values and sums remain safe integers.

**Domain:** `last` and `now` are nonnegative safe integer timestamps in the same
unit; `timeout` is a positive integer represented by a finite JavaScript `Number`.
`result` is the Boolean returned by `expired(last, now, timeout)`.

**Assumptions:** the logical statement uses mathematical integer arithmetic.
The implementation uses JavaScript `Number` arithmetic, so a check must account
for that representation. This function compares supplied timestamps; it does not
read a clock. The translation property applies when all translated values and
sums remain safe integers.

**Logical statement (postcondition):** for every input in the domain, on return,
`result` is true if and only if `now >= last + timeout`.

**Test search:** timestamps and shifts range from zero to one billion; timeouts
range from one to one million. Explicit postcondition examples cover equality and
later expiration. Generated values and sums stay within the safe integer domain.
These ranges bound the search, not the requirement.

Needs: impl, utest
