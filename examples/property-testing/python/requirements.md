# Expiration

`req~expiration~1`

For integer timestamps and a positive integer timeout, a session is expired
when the current time is at least the last-activity time plus the timeout.
Equality expires the session. Shifting both timestamps by the same integer
does not change the expiration decision. Test generators use nonnegative
timestamps up to one billion and timeouts from one to one million.

Needs: impl, utest
