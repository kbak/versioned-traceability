# Model checking

Use Alloy for relational and state-machine properties and Z3 for arithmetic or
other SMT theories recovered during onboarding. The [model-checking skill](../versioned_traceability/skills/model-checking/SKILL.md)
guides Codex to derive assertions from requirements and a native `.als` or Z3Py abstraction
from their implementation. Store those models and their replay tests in the
application repository, linked to the existing requirement revisions.

The tool reuses [Z3](https://github.com/Z3Prover/z3) and [Alloy 6.2.0](https://github.com/AlloyTools/org.alloytools.alloy/releases/tag/v6.2.0)
and bundled SAT4J. No model-generation service, MCP server, source compiler or
new property language is required. Z3 is an optional pinned Python package extra. The deterministic CLI accepts a small manifest
of exact commands and explicitly captured input files. Its
[execution reference](../versioned_traceability/skills/model-checking/references/execution.md)
defines the Alloy manifest, commands, exit meanings and retained evidence; the
[SMT reference](../versioned_traceability/skills/model-checking/references/smt.md)
defines native Z3Py obligations and `vt smt-check`.

## Results and correspondence

For Alloy assertions, SAT is a counterexample and UNSAT means no counterexample within
the native bounds. For witness runs, SAT is required; UNSAT rejects a model that
cannot exhibit the selected required behavior. Missing commands, wrong command
kinds, malformed results, timeouts and solver failures are errors. A successful
Java process alone is insufficient. Witnesses detect some empty/overconstrained
models, but cannot establish specification adequacy by themselves.

Z3 first requires satisfiable assumptions, then checks the negated goal. UNSAT
establishes that goal under the encoding's assumptions. Numeric domains can cover
the entire source type while contract counts or transition depth remain bounded.
Required SAT witnesses exercise important branches. `unknown` is inconclusive
and produces an error. Native SMT-LIB queries and exact model observations are
retained for independent inspection and implementation replay.

The model's interpretation still needs review. Document its state, initial
conditions, permitted transitions, frame conditions, arithmetic and environment
assumptions, mapping to code, and omitted behavior. Replay generated traces and
compare state after each implementation step. Deliberate model and implementation
mutations provide sensitivity evidence. These steps are not an equivalence proof
or a soundness proof for a general source-to-model translation.

## Integration

`vt alloy-check` writes `result.json`, `junit.xml`, native receipts and XML instances,
logs and copies of selected inputs. JUnit embeds native receipts/traces and input
metadata so ordinary `vt check` retention preserves them. Standalone results bind
only listed inputs. The enclosing `vt check` supplies whole-candidate identity and
the existing requirement revision/review policy.

`vt smt-check` similarly retains native SMT-LIB queries, model receipts, source
hashes and JUnit. Both runners retain per-command outcomes.

Run the selected backend alongside the project's normal test command and include the fresh
report in `tests.reports`. Include models, manifests, mappings and replay harnesses
in the test scope. Declare optional named OFT artifacts in a supported file rather
than assuming `.als` annotations are imported. Use the existing required-execution
policy for selected model artifacts after the scope is reviewed and adopted.
