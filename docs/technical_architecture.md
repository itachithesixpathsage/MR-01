# Technical architecture

`data` parses and validates local CSV; `indicators` contains pure indicator functions; `strategy` performs regime, signal, and position-sizing calculations; `variants` identifies the two independent timing conventions; `reporting` writes outputs and provenance; `cli` orchestrates workflows. No module can place trades or access a broker.

Calculations use pandas/NumPy float64. A run invokes one variant. Comparison joins separately calculated outputs and retains suffixes. `run_manifest.json` hashes both inputs and records ranges, parameters, software and warnings.
