# Standalone setup for implementation

Discussion alone does not require installing or running tooling. For authorized
implementation, use the chosen tool checkout/revision and its matching skill.
When only a skill link is supplied, clone its repository/ref over HTTPS into a
new directory outside the target project and resolve it to a commit. For an
unversioned copy without a supplied source, use
`https://github.com/kbak/versioned-traceability.git` at main. Reread the matching
skill and references, and retain the tooling revision for the handoff.
Resolve relative references there, not in the target project. Reuse a supplied
local checkout, packaged skill/runtime or inline reference when available. If an
installed vt cannot be tied to that source, install from the chosen checkout into
a fresh external environment; a version number alone does not establish a match.

The runtime needs Python 3.11+, Git, Java 17+, the portable package and the target
project's test dependencies. Keep tool checkouts and environments outside the target
project and preserve existing local work. After choosing absolute paths in
vt_checkout and vt_env:

```sh
python3 -m venv "$vt_env"
"$vt_env/bin/python" -m pip install "$vt_checkout"
"$vt_env/bin/python" -m versioned_traceability check --help
"$vt_env/bin/python" -m versioned_traceability verify --help
"$vt_env/bin/python" -m versioned_traceability install-oft
```

Reuse an existing pinned OFT JAR via VT_OFT_JAR when available. Use the same
interpreter for checks and verification, with an explicit target --repo after
setup. Prepare the project's real test runner using its instructions; installing
vt does not install those dependencies. Resolve routine setup within task
permissions and report concrete blockers. Do not change project dependency
manifests solely to install the checker or silently substitute an unavailable
requested tool revision.
