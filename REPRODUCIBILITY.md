# Reproducibility scope

This public release is based on the final manuscript and frozen analysis files
retained on October 17, 2026. It is not the earlier E1–E4 anonymous artifact.

## Included

- 36 inputs: 30 original materials and six decimal materials.
- Six recorded model IDs, three repeats, three verification configurations and
  three exchange scenarios, giving 5,832 retained logical trial slots.
- Original outcome decisions and success flags; source group and physical run
  locator retained for each row.
- All nine aggregate numerator/denominator pairs and the recorded material
  bootstrap, reproduced by `python -m scripts.reproduce`.
- The unmodified canonicalization core and its versioned resource limits.
- A standalone adapter that extracts the proposed verification behavior from
  the original implementation. It has no A/B legacy-harness dependency and is
  not claimed to be the original full experiment harness.
- Tests of all 36 materials and numeric, Unicode, reference and rejection cases.

## Selection and version provenance

The main results include schema-compliant original measurements or the one
explicitly authorized format retest for the same logical slot. A compliant wrong
answer remains an error. Retests do not add independent repeats. The decimal
experiment uses a separately versioned profile. The combined paper analysis
contains 30 original materials and six decimal materials; bridge measurements
are excluded. Historical trials have not been silently relabelled as executions
of the decimal profile.

See the manuscript's experimental-method disclosure for the selection rule.
The CSV success flags are retained graded outcomes. The public analysis checks
pairing and aggregation, but cannot independently validate every grade without
the underlying transcripts. Recorded model IDs identify historical executions;
they are not a claim about current provider availability.

## Not included in version 1.0.0

The complete agent transcripts, gateway evidence, original response and format
retest ledgers, version-bridge run, container images and launch environment are
not bundled. Their full archive was on an external volume unavailable when this
release was assembled. This release therefore does not claim end-to-end live
experiment reproducibility. Adding that archive requires a separate reviewed
release; the historical paths in `physical_source` are not downloadable links.

## Integrity checks

`provenance.json` records copied source files byte for byte. `SHA256SUMS` covers
the release payload excluding itself and transient build outputs. The offline
reproduction script checks the research-source hashes before computing results.
A matching release hash detects changed bytes; it does not establish independent
authenticity or validate a research claim.
