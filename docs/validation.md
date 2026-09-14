# Running the tests

From the project checkout, in a Python virtual environment with Git and Java
available:

```sh
python3 -m pip install -e . ruff
vt install-oft
python3 -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

Tests run OFT and example test commands in temporary Git repositories. A missing
OFT JAR fails the suite. To use an existing JAR, set `VT_OFT_JAR` instead of running
`vt install-oft`.
