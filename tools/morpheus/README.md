# Morpheus

The morphology in `../data/morph-morpheus` was produced by the Morpheus
morphological analyzer (MPL-2.0), used through the Python toolkit:

* https://github.com/QuantForgeSoftware/morpheus — the analyzer
* `python/morpheus_toolkit/` — the toolkit (`Morpheus`, `analyze_tokens`, …)

To rebuild, point the analyzer at a checkout of the toolkit:

```bash
MORPHEUS_PY=/path/to/morpheus/python \
  /path/to/morpheus/.venv/bin/python ../code/python/analyze_lxx.py
```

The toolkit needs its own virtualenv because it depends on `beta_code`.
