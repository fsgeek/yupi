# Corpus manifests

One JSON per corpus run, written by `scripts/corpus_generate.py`. The
manifest is the record (design v0.1 §5): with it and the code at its
`generator_version`, `scripts/corpus_generate.py --from-manifest <file>`
regenerates the corpus byte for byte (gate 1). Corpora themselves live
under `corpus/` (gitignored). The run key is provenance, not a secret
from us; the model never sees the renaming table.
