# Same Data, Different Bytes

**Serialization-Invariant Integrity Checks for Agent-Published Datasets**  
Jin Gao and Maura Clark · IEEE TPS 2026 NANDA Workshop · Paper 6819

Public supplementary material for the final October 17, 2026 manuscript.
The paper asks how a reader agent can distinguish equivalent JSON re-encoding
from altered content when checking a received dataset against its owner's record.

```text
{"units":34}  →  {"units":34.0}
Same numeric value; the existing JSON checksum differs.
The proposed comparison normalizes supported representations and checks that
canonicalization preserves exact numeric values before hashing.
```

## Start here

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m scripts.demo
python -m unittest discover -s tests -v
python -m scripts.reproduce
```

Python 3.10 or newer. Reproduction runs locally without credentials, Docker,
a model endpoint, or a running DataFacts service. The analysis writes CSV tables
to `build/`, verifies all nine paper aggregate counts, and recomputes the recorded
100,000-resample paired material bootstrap.

## Contents and scope

| Location | Contents |
|---|---|
| [`paper/author-manuscript.pdf`](paper/author-manuscript.pdf) | Author manuscript prepared for arXiv |
| [`paper/source/`](paper/source/) | LaTeX source, original Figure 1 and Algorithm 1 |
| [`decimal_extension/`](decimal_extension/) | Unmodified exact-decimal canonicalization core and profile limits |
| [`verification.py`](verification.py) | Standalone adapter for the proposed verification path |
| [`data/materials.json`](data/materials.json) | All 36 JSON materials, with original, equivalent and altered representations |
| [`data/trials.csv`](data/trials.csv) | All 5,832 retained trial-level outcome records used for the final aggregate results |
| [`data/`](data/) | Frozen aggregate counts, bootstrap intervals, model metadata and deterministic probes |
| [`scripts/`](scripts/) | Offline demonstration and table/uncertainty reproduction |
| [`provenance.json`](provenance.json) | Source paths and SHA-256 hashes for copied research files |

This release supports **algorithm inspection, deterministic validation, and
reproduction of the published aggregates from retained outcome records**.
It does **not** include the complete raw agent conversations, original gateway
logs, frozen deployment, or a turnkey rerun of the live model experiments.
The `physical_source` column records the historical run location, not a path
bundled in this release. The `success` column is an existing graded outcome;
recomputing aggregate rates does not independently re-grade the conversations.

The original full run archive is not part of this public release. Its absence is
recorded in [REPRODUCIBILITY.md](REPRODUCIBILITY.md). No new model trials are
presented as historical measurements. The older development repository contains
an earlier experimental design and is not the release backing this manuscript.

## AgentFacts, DataFacts and Algorithm 1

AgentFacts describes agent identity, protocols and skills. In the integration
used here, `datafacts_url` points to the agent's DataFacts configuration.
DataFacts describes datasets, access conditions and checksum evidence;
`data_owner` identifies the owning agent. Discovery and access negotiation
precede content verification and are separate from this algorithm.

Algorithm 1 takes original JSON bytes and an authentic owner's reference record:

1. Check reference availability and processing-profile compatibility.
2. Parse exact decimals; normalize strings and keys using Unicode NFC.
3. Prepare supported numbers and serialize using JCS (RFC 8785).
4. Reparse the canonical bytes and compare the normalized JSON trees exactly.
5. Only if values are preserved, hash and compare with the owner's identifier.

Possible results are `match`, `mismatch`, `unavailable`, `invalid_input`, and
`unsupported_input`. A precision-loss failure is unsupported, not a mismatch.
The supported profile has finite numeric and resource bounds; it is not an
arbitrary-precision decimal serializer. Owner authentication is an assumption,
not a feature provided by this standalone verifier.

## Reported outcomes

Each cell has 648 retained trials. A = ordinary tools, B = existing checksum,
C = proposed comparison. These are the selected outcomes described in the paper,
not unconditional first-attempt success rates.

| Scenario and expected outcome | A | B | C |
|---|---:|---:|---:|
| Equivalent re-encoding: accept and answer correctly | 18.4% | 28.5% | 98.8% |
| Altered content: evidence-supported rejection | 65.9% | 93.8% | 97.4% |
| Unavailable reference: evidence-supported abstention | 99.2% | 99.5% | 99.5% |

The analysis keeps all models, repeats, arms and scenarios together when
resampling each material. Its intervals describe empirical material-resampling
uncertainty conditional on this model set and selected material mix.

## Attribution and license

The original canonicalization component is authored by Maura Clark and vendored
unchanged from [`maurathat/canonical-dataset-lineage`](https://github.com/maurathat/canonical-dataset-lineage),
through [`maurathat/custody`](https://github.com/maurathat/custody).
See [`vendor/canon/NOTICE`](vendor/canon/NOTICE) and
[`vendor/canon/CANON_PROVENANCE`](vendor/canon/CANON_PROVENANCE) for pinned commits.

The project code follows the Apache-2.0 license of the existing project;
third-party notices remain applicable. The manuscript and its figures are
research publications, not relicensed as software. See [LICENSE](LICENSE),
[NOTICE](NOTICE), and [CITATION.cff](CITATION.cff).
