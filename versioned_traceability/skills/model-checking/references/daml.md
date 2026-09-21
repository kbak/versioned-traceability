# Daml implementation correspondence

Select a contract lifecycle with existing Daml Script tests. For split/merge
operations, check quantity conservation, authorization, input consumption, and
preservation of owner and business identity.

Inspect the pinned SDK/LF version, template/interface implementations, controller
and signatory expressions, consuming versus nonconsuming choices, and nested
exercises. Model active contracts and party relationships explicitly. Track
authorization context through a transaction; a controller name alone does not
capture Daml authorization. Include rejected transactions and atomic rollback.
Do not model rejection by assuming every submitted operation is authorized.

Use exact integer quanta for bounded quantities and relate them to the actual
`Numeric` scale, representable range, rounding and rejection behavior. Small Alloy
integer scopes cannot establish the full decimal arithmetic contract. Preserve
nonnegative/positive input distinctions and zero/remainder cases.

Replay via Daml Script against a fresh IDE ledger for each trace, building the
test DAR with the project's pinned SDK. Query active output contracts and consumed
inputs, submit under the modeled parties, and check expected failures. Reuse the
project's existing generated-input driver when available. Retain
DAR digest, SDK version, inputs, native diagnostics and JUnit results. A pure
Python simulation cannot validate ledger authorization or contract consumption.

Start with single-ledger transaction semantics. State explicitly that participant
visibility, distributed Canton behavior, external valuations and orchestration
are outside that slice unless separately modeled and exercised.
