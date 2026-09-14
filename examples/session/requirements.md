# Session expiration

### Inactivity timeout
`req~session-expiration~1`

A session expires when its inactivity reaches 30 minutes. A session with less
than 30 minutes of inactivity remains active.

Needs: impl, utest
